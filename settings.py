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

<<<<<<< HEAD
# DB_CONFIG = {
#   "PSQL": {
#     "HOST": os.getenv("ZTF_HOST"),
#     "DB_NAME": os.getenv("ZTF_DATABASE"),
#     "USER": os.getenv("ZTF_USER"),
#     "PASSWORD": os.getenv("ZTF_PASSWORD"),
#     "PORT": ***REMOVED***,
#   }
# }


host = "***REMOVED***"
db_name = "***REMOVED***"
user = "***REMOVED***"
password = "***REMOVED***"
port = ***REMOVED***
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
=======
HOST = os.getenv("DB_HOST", "localhost") #"3.226.200.73"
DATABASE = os.getenv("DB_DATABASE", "postgres") #"new_pipeline"
USER = os.getenv("DB_USER", "postgres") #"***REMOVED***"
PASSWORD = os.getenv("DB_PASSWORD", "password") #"***REMOVED***"
PORT = os.getenv("DB_PORT",***REMOVED***)
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
>>>>>>> 0e3cf540f920f4864da7d5a8298773e1005bd029
DATABASE = {
    "SQL": {
        "SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL
    }
}
