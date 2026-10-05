import asyncio
import time

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.concurrency import ConcurrencyLimitMiddleware, is_exempt


def make_app(max_concurrent: int, queue_wait_seconds: float) -> FastAPI:
    app = FastAPI()
    app.add_middleware(ConcurrencyLimitMiddleware, max_concurrent=max_concurrent, queue_wait_seconds=queue_wait_seconds)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/slow")
    def slow(seconds: float = 0.5):
        time.sleep(seconds)
        return "done"

    @app.get("/healthcheck")
    def healthcheck():
        return "OK"

    return app


async def _gather(app, *paths, headers=None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await asyncio.gather(*(client.get(p, headers=headers) for p in paths))


def test_is_exempt():
    assert is_exempt("/")
    assert is_exempt("/healthcheck")
    assert is_exempt("/metrics")
    assert is_exempt("/htmx/htmx.min.js")
    assert is_exempt("/v/0.2.11/static/search_form/form_search.js")
    assert not is_exempt("/htmx/list_objects")
    assert not is_exempt("/stamp")


def test_requests_within_the_cap_run_at_the_same_time():
    app = make_app(max_concurrent=3, queue_wait_seconds=2)
    start = time.perf_counter()
    responses = asyncio.run(_gather(app, "/slow", "/slow", "/slow"))
    elapsed = time.perf_counter() - start

    assert [r.status_code for r in responses] == [200, 200, 200]
    # One after another would take 1.5 s.
    assert elapsed < 1.2


def test_requests_over_the_cap_wait_then_get_503():
    app = make_app(max_concurrent=1, queue_wait_seconds=0.2)
    responses = asyncio.run(_gather(app, "/slow?seconds=1", "/slow?seconds=1", headers={"Origin": "https://x.org"}))

    statuses = sorted(r.status_code for r in responses)
    assert statuses == [200, 503]
    busy = next(r for r in responses if r.status_code == 503)
    assert busy.headers["retry-after"] == "1"
    # CORS wraps the cap, so a browser can read the 503.
    assert busy.headers["access-control-allow-origin"] == "*"


def test_a_waiting_request_gets_the_slot_when_it_frees_up():
    app = make_app(max_concurrent=1, queue_wait_seconds=2)
    responses = asyncio.run(_gather(app, "/slow?seconds=0.3", "/slow?seconds=0.3"))
    assert [r.status_code for r in responses] == [200, 200]


def test_exempt_paths_skip_the_cap():
    app = make_app(max_concurrent=1, queue_wait_seconds=0.1)

    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            slow = asyncio.create_task(client.get("/slow?seconds=1"))
            await asyncio.sleep(0.2)  # the slow request holds the only slot
            start = time.perf_counter()
            health = await client.get("/healthcheck")
            health_seconds = time.perf_counter() - start
            await slow
            return health, health_seconds

    health, health_seconds = asyncio.run(run())
    assert health.status_code == 200
    assert health_seconds < 0.5
