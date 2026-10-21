from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.error_handlers import add_error_handlers
from core.version import APP_VERSION

from .routes import rest

# root_path: the prefix nginx strips, so /docs fetches /features_api/openapi.json (static files: core/static_files.py)
app = FastAPI(
    root_path="/features_api",
    title="ALeRCE Features API",
    version=APP_VERSION,
    description="Light-curve features of ZTF and LSST objects, the input of the light-curve classifier.",
    contact={"name": "ALeRCE", "url": "https://alerce.science"},
)
add_concurrency_limit(app)
add_error_handlers(app)
psql_engine = psql_entity()
app.state.psql_session = psql_engine.session

app.include_router(rest.router)

app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
