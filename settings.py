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
#     "PORT": ***REMOVED***,
#   }
# }

DB_CONFIG = {
  "PSQL": {
    "HOST": "18.211.226.219",
    "DB_NAME": "new_pipeline",
    "USER": "***REMOVED***",
    "PASSWORD": "***REMOVED***",
    "PORT": ***REMOVED***,
  }
  # "SQLITE": {

  # }
}