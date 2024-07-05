from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import htmx, rest
from database.sql import connect as connect_sql, session_wrapper

app = FastAPI(openapi_url="/v2/lightcurve/openapi.json")
app.state.mongo_db = None
psql_engine = connect_sql()
app.state.psql_session = session_wrapper(psql_engine)
instrumentator = Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(prefix="/htmx", router=htmx.router)

app.mount("/static", StaticFiles(directory="src/banner_api/static"), name="static")


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
