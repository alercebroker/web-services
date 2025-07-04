from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from core.config.connection import psql_entity
from .routes import rest

app = FastAPI(openapi_url="/v2/lightcurve/openapi.json")
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

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(rest.router, prefix="/multisurvey")

app.mount(
    "/static",
    StaticFiles(directory="src/lightcurve_api/static"),
    name="static",
)


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
