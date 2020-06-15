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

# DB_CONFIG = {
#   "PSQL": {
#     "HOST": os.getenv("ZTF_HOST"),
#     "DB_NAME": os.getenv("ZTF_DATABASE"),
#     "USER": os.getenv("ZTF_USER"),
#     "PASSWORD": os.getenv("ZTF_PASSWORD"),
#     "PORT": 5432,
#   }
# }


host = "3.226.200.73"
db_name = "new_pipeline"
user = "alerce"
password = "ETgW4GTdR337gjP7"
port = 5432
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
DATABASE = {
    "SQL": {
        "SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL
    }
}

