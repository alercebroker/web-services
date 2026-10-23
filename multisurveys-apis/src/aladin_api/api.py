from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.static_files import mount_static
from core.version import APP_VERSION

from .routes import htmx, rest

# root_path: the prefix nginx strips, so /docs fetches /aladin_api/openapi.json (static files: core/static_files.py)
app = FastAPI(root_path="/aladin_api", title="ALeRCE Aladin API", version=APP_VERSION)
add_concurrency_limit(app)
add_error_handlers(app)
psql = psql_entity()
app.state.psql_session = psql.session


app.include_router(rest.router)
app.include_router(htmx.router, tags=["Browser UI (HTMX)"])


static_path = Path(__file__).resolve().parent / "static"
mount_static(app, "/static", static_path, "static")
mount_static(app, "/htmx", "src/core/htmx", "htmx")

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
