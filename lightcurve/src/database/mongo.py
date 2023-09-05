import os
from pymongo import MongoClient

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
    "authSource": db,
}
database_name = config.pop("database")
client = MongoClient(**config)
database = client[database_name]
