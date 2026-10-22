from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.static_files import mount_static
from core.version import APP_VERSION

from .routes import htmx, rest

# root_path: the prefix nginx strips, so /docs fetches /magstat_api/openapi.json (static files: core/static_files.py)
app = FastAPI(root_path="/magstat_api", title="ALeRCE Magstat API", version=APP_VERSION)
add_concurrency_limit(app)
add_error_handlers(app)
psql_engine = psql_entity()
app.state.psql_session = psql_engine.session
instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False)


mount_static(app, "/static", "src/magstat_api/static", "static")
mount_static(app, "/htmx-static", "src/core/htmx", "htmx-static")

app.include_router(rest.router)
app.include_router(htmx.router, tags=["Browser UI (HTMX)"])

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
