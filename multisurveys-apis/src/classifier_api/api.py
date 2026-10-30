from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.version import APP_VERSION

from .routes import rest

app = FastAPI(title="ALeRCE Classifier API", version=APP_VERSION)
add_concurrency_limit(app)
add_error_handlers(app)
psql_engine = psql_entity()
app.state.psql_session = psql_engine.session
instrumentator = Instrumentator().instrument(app).expose(app, include_in_schema=False)


app.include_router(rest.router)

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
