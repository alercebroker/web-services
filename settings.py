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

HOST = os.getenv("DB_HOST", "localhost") #"3.226.200.73"
DATABASE = os.getenv("DB_DATABASE", "postgres") #"new_pipeline"
USER = os.getenv("DB_USER", "postgres") #"alerceread"
PASSWORD = os.getenv("DB_PASSWORD", "password") #"alerce2020"
PORT = os.getenv("DB_PORT",5432)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
DATABASE = {
    "SQL": {
        "SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL
    }
}
