from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.config.connection import connect as connect_sql
from core.config.connection import session_wrapper, psql_entity

from .routes import rest

app = FastAPI()

psql = psql_entity()
app.state.psql_session = psql.session
instrumentator = Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest.router)
