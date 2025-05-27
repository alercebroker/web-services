from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from core.config.connection import connect as connect_sql
from core.config.connection import session_wrapper
from .routes import rest

app = FastAPI()

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

app.include_router(rest.router)

app.mount(
    "/static", StaticFiles(directory="src/object_api/static"), name="static"
)


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()