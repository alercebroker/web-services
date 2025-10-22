from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import rest, htmx
from core.config.connection import psql_entity

app = FastAPI(openapi_url="/stamps/openapi.json")
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
app.mount("/static", StaticFiles(directory="src/stamps_api/static"), name="static")


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
