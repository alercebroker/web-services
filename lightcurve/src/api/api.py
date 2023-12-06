import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from ralidator_fastapi.ralidator_fastapi import RalidatorStarlette

from .filters import get_filters_map
from .routes import htmx, rest

app = FastAPI(openapi_url="/v2/lightcurve/openapi.json")
instrumentator = Instrumentator().instrument(app).expose(app)


if os.getenv("ENV") != "dev":
    app.add_middleware(
        RalidatorStarlette,
        config={"SECRET_KEY": os.getenv("SECRET_KEY")},
        filters_map=get_filters_map(),
        ignore_paths=[
            "/docs",
            "/metrics",
            "/openapi.json",
        ],
        ignore_prefixes=[
            "/static",
            "/htmx",
        ],
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest.router)
app.include_router(prefix="/htmx", router=htmx.router)

app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
