import os

from pymongo import MongoClient
from pymongo.database import Database

user = os.getenv("MONGO_USER", "")
pwd = os.getenv("MONGO_PASSWORD", "")
host = os.getenv("MONGO_HOST")
port = os.getenv("MONGO_PORT", "27017")
db = os.getenv("MONGO_DATABASE")
auth_source = os.getenv("MONGO_AUTH_SOURCE")

config = {
    "host": host,
    "serverSelectionTimeoutMS": 3000,  # 3 second timeout
    "port": int(port),
    "database": db,
    "username": user,
    "password": pwd,
}

if auth_source:
    config["authSource"] = auth_source

database_name = config.pop("database")

def connect() -> Database:
    print("connecting with config", config)
    client = MongoClient(**config)
    database = client[database_name]
    return database
