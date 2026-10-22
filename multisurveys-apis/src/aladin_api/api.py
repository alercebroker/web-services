from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.static_files import mount_static

from .routes import htmx, rest

app = FastAPI()
add_concurrency_limit(app)
add_error_handlers(app)
psql = psql_entity()
app.state.psql_session = psql.session


app.include_router(rest.router)
app.include_router(htmx.router)


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
