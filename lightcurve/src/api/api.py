from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from ralidator_fastapi.ralidator_fastapi import RalidatorStarlette

from .filters import get_filters_map
from .routes import htmx, rest, period, object
from config import app_config
from database.mongo import connect as connect_mongo
from database.sql import connect as connect_sql, session_wrapper

app = FastAPI(openapi_url="/v2/lightcurve/openapi.json")
app.state.mongo_db = None
psql_engine = connect_sql()
app.state.psql_session = session_wrapper(psql_engine)
instrumentator = Instrumentator().instrument(app).expose(app)
config = app_config()

app.add_middleware(
    RalidatorStarlette,
    config=config["ralidator"],
    filters_map=get_filters_map(),
    ignore_paths=config["ralidator"]["ignore_paths"],
    ignore_prefixes=config["ralidator"]["ignore_prefixes"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(rest.router)
app.include_router(prefix="/htmx", router=htmx.router)
app.include_router(prefix="/period", router=period.router)
app.include_router(prefix="/object", router=object.router)
app.include_router(prefix="/magStat", router=object.router)

app.mount("/static", StaticFiles(directory="src/api/static"), name="static")


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
