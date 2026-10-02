from fastapi import FastAPI
from core.concurrency import add_concurrency_limit
from core.static_files import mount_static
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from core.config.connection import psql_entity
from .routes import rest, htmx

app = FastAPI()
add_concurrency_limit(app)
psql_engine = psql_entity()
app.state.psql_session = psql_engine.session
instrumentator = Instrumentator().instrument(app).expose(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mount_static(app, "/static", "src/magstat_api/static", "static")
mount_static(app, "/htmx-static", "src/core/htmx", "htmx-static")

app.include_router(rest.router)
app.include_router(htmx.router)
