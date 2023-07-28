from fastapi import FastAPI
from core.service import get_detections, get_non_detections, get_lightcurve
from database.sql import PsqlDatabase
from database.mongo import MongoDatabase
from .result_handler import handle_success, handle_error
import os

app = FastAPI()

user = os.getenv("PSQL_USER")
pwd = os.getenv("PSQL_PASSWORD")
host = os.getenv("PSQL_HOST")
port = os.getenv("PSQL_PORT")
db = os.getenv("PSQL_DATABASE")
url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
psql_database = PsqlDatabase(url)
user = os.getenv("MONGO_USER")
pwd = os.getenv("MONGO_PASSWORD")
host = os.getenv("MONGO_HOST")
port = os.getenv("MONGO_PORT")
db = os.getenv("MONGO_DATABASE")
config = {
    "host": host,
    "serverSelectionTimeoutMS": 3000,  # 3 second timeout
    "username": user,
    "password": pwd,
    "port": int(port),
    "database": db,
}
mongo_database = MongoDatabase(config)


@app.get("/")
async def root():
    return "this is the lightcurve module"


@app.get("/detections/{oid}")
async def detections(oid: str, survey_id: str = "ztf"):
    return get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=psql_database.session,
        mongo_db=mongo_database.database,
        handle_error=handle_error,
        handle_success=handle_success,
    )


@app.get("/non_detections/{oid}")
async def non_detections(oid: str, survey_id: str = "ztf"):
    return get_non_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=psql_database.session,
        mongo_db=mongo_database.database,
        handle_error=handle_error,
        handle_success=handle_success,
    )


@app.get("/lightcurve/{oid}")
async def lightcurve(oid: str, survey_id: str = "ztf"):
    return get_lightcurve(
        oid=oid,
        survey_id=survey_id,
        session_factory=psql_database.session,
        mongo_db=mongo_database.database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
