"""
A per-pod cap on the requests that reach the route handlers.

Route handlers are plain ``def`` and run in a thread pool, so one pod can serve several requests at once. Each
API has a fixed budget of database connections behind PgBouncer, so this middleware lets at most
``MAX_CONCURRENT_REQUESTS`` requests in at a time. Others wait up to ``QUEUE_WAIT_SECONDS`` for a slot and then
get ``503`` with ``Retry-After: 1``: when the database link stalls, telling the browser "busy" right away beats
holding it for PgBouncer's 30 s error.

Pings, health checks, ``/metrics`` and static files skip the cap. Static files are recognised by their file
extension rather than by path prefix, because ``/htmx/`` holds both ``htmx.min.js`` and real routes such as
``/htmx/list_objects``.

Both values are environment variables, set in the ``environment:`` block of each API's ``config.yaml``.
"""

import asyncio
import os

import anyio.to_thread
from fastapi import FastAPI
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

DEFAULT_MAX_CONCURRENT_REQUESTS = 5
DEFAULT_QUEUE_WAIT_SECONDS = 2.0
# Threads beyond the cap, so static files and /metrics (which also use the thread pool) never wait behind slow
# requests.
EXTRA_THREADS = 10

EXEMPT_PATHS = {"/", "/healthcheck", "/metrics", "/docs", "/openapi.json"}
STATIC_EXTENSIONS = (".js", ".mjs", ".css", ".map", ".woff", ".woff2", ".ttf", ".svg", ".ico")


def is_exempt(path: str) -> bool:
    return path in EXEMPT_PATHS or path.endswith(STATIC_EXTENSIONS)


class ConcurrencyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_concurrent: int, queue_wait_seconds: float):
        self.app = app
        self.max_concurrent = max_concurrent
        self.queue_wait_seconds = queue_wait_seconds
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._thread_pool_sized = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if not self._thread_pool_sized:
            # The thread limiter belongs to the running event loop, so it can only be set from inside it.
            anyio.to_thread.current_default_thread_limiter().total_tokens = self.max_concurrent + EXTRA_THREADS
            self._thread_pool_sized = True

        if is_exempt(scope["path"]):
            await self.app(scope, receive, send)
            return

        try:
            await asyncio.wait_for(self._semaphore.acquire(), timeout=self.queue_wait_seconds)
        except TimeoutError:
            response = PlainTextResponse("Service busy, please retry", status_code=503, headers={"Retry-After": "1"})
            await response(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        finally:
            self._semaphore.release()


def add_concurrency_limit(app: FastAPI):
    """
    Install the cap. Call it before adding CORSMiddleware: the middleware added last is the outermost, and CORS
    must wrap the 503 so browsers can read it.
    """
    app.add_middleware(
        ConcurrencyLimitMiddleware,
        max_concurrent=int(os.getenv("MAX_CONCURRENT_REQUESTS", DEFAULT_MAX_CONCURRENT_REQUESTS)),
        queue_wait_seconds=float(os.getenv("QUEUE_WAIT_SECONDS", DEFAULT_QUEUE_WAIT_SECONDS)),
    )
