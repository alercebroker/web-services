from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from core.error_handlers import add_error_handlers
from core.static_files import mount_static
from core.version import APP_VERSION

from . import htmx
from .router import router

# root_path: the prefix nginx strips, so /docs fetches /status_api/openapi.json
app = FastAPI(
    root_path="/status_api",
    title="ALeRCE Status API",
    version=APP_VERSION,
    description="Is each ALeRCE pipeline up to date, and how many alerts it received and processed recently.",
)
add_concurrency_limit(app)
add_error_handlers(app)
instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(router)
app.include_router(htmx.router, tags=["Browser UI (HTMX)"])

mount_static(app, "/static", "src/status_api/static", "static")
mount_static(app, "/htmx", "src/core/htmx", "htmx")

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
