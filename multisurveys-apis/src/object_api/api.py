from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.static_files import mount_static
from core.version import APP_VERSION

from .routes import htmx, rest

# root_path: the prefix nginx strips, so /docs fetches /object_api/openapi.json (static files: core/static_files.py)
app = FastAPI(root_path="/object_api", title="ALeRCE Object API", version=APP_VERSION)
add_concurrency_limit(app)
add_error_handlers(app)

psql = psql_entity()
app.state.psql_session = psql.session
instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(rest.router)
app.include_router(htmx.router, tags=["Browser UI (HTMX)"])


static_path = Path(__file__).resolve().parent / "static"
mount_static(app, "/static", static_path, "static")

mount_static(app, "/htmx", "src/core/htmx", "htmx")

mount_static(app, "/libraries", "src/core/libraries", "libraries")

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
