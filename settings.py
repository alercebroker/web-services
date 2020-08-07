import os


PROFILE = False

PROFILE_CONFIG = {
    "enabled": PROFILE,
    "storage": {
        "engine": "sqlite"
    },
    "basicAuth":{
        "enabled": True,
        "username": "admin",
        "password": "admin"
    },
    "ignore": [
	    "^/static/.*"
	]
}

HOST = os.getenv("DB_HOST", "localhost")
DATABASE = os.getenv("DB_DATABASE", "postgres")
USER = os.getenv("DB_USER", "postgres") 
PASSWORD = os.getenv("DB_PASSWORD", "password")
PORT = os.getenv("DB_PORT",5432)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

DATABASE = {
    "SQL": {
        "SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL
    }
}
