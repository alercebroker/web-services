from fastapi import FastAPI, HTTPException
from database.database import create_connection
import os
from typing import List, Literal
from core.service import get_oids_from_coordinates, Mastercat

app = FastAPI()
user = os.getenv("DB_USER")
pwd = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", 5432)
db = os.getenv("DB_DATABASE", "xmatch")
pool = create_connection(user, pwd, host, port, db)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/conesearch")
def conesearch(ra: float, dec: float, radius: float, cat: Literal["all", "wise", "vlass", "lsdr10"]="all") -> List[Mastercat]:
    if radius <= 0:
        raise HTTPException(status_code=422, detail="Radius should be greater than 0")
    return get_oids_from_coordinates(ra, dec, radius, pool, cat)

