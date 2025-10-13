from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from core.config.connection import psql_entity
from .routes import rest, htmx

app = FastAPI()
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

app.include_router(rest.router)
app.include_router(htmx.router)

app.mount("/static", StaticFiles(directory="src/crossmatch_api/static"), name="static")
app.mount("/htmx", StaticFiles(directory="src/core/htmx"), name="htmx")
