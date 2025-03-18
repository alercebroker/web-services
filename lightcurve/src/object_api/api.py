from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from database.sql import connect as connect_sql
from database.sql import session_wrapper

from .routes import htmx, rest

app = FastAPI(openapi_url="/v2/object/openapi.json")
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


app.include_router(rest.router)
app.include_router(prefix="/htmx", router=htmx.router)

app.mount(
    "/static", StaticFiles(directory="src/object_api/static"), name="static"
)

app.mount(
    "/htmx", StaticFiles(directory="src/core/static/htmx"), name="htmx"
)

@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
