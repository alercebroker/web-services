from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.concurrency import add_concurrency_limit
from core.config.connection import psql_entity
from core.static_files import mount_static

from .routes import htmx, rest

app = FastAPI(openapi_url="/stamps/openapi.json")
add_concurrency_limit(app)
psql = psql_entity()
app.state.psql_session = psql.session

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest.router)
app.include_router(htmx.router, prefix="/htmx")

# Mount static files
mount_static(app, "/static", "src/stamps_api/static", "static")
mount_static(app, "/htmx-static", "src/core/htmx", "htmx-static")


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
