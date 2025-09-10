from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from .routes.htmx import lightcurve as htmx_lightcurve
from .routes.json import conesearch, lightcurve as json_lightcurve

app = FastAPI(openapi_url="/v2/lightcurve/openapi.json")
instrumentator = Instrumentator().instrument(app).expose(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(json_lightcurve.router)
app.include_router(conesearch.router)

app.mount(
    "/static",
    StaticFiles(directory="src/static"),
    name="static",
)


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
