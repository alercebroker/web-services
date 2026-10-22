from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.static_files import mount_static

from .routes import htmx, rest

app = FastAPI()
add_concurrency_limit(app)
add_error_handlers(app)
psql_engine = psql_entity()
app.state.psql_session = psql_engine.session
instrumentator = Instrumentator().instrument(app).expose(app)


mount_static(app, "/static", "src/magstat_api/static", "static")
mount_static(app, "/htmx-static", "src/core/htmx", "htmx-static")

app.include_router(rest.router)
app.include_router(htmx.router)

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
