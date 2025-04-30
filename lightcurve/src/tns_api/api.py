from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import rest
from database.sql import connect as connect_sql
from database.sql import session_wrapper

app = FastAPI()
psql_engine = connect_sql()
app.state.psql_session = session_wrapper(psql_engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(rest.router)