import os


PROFILE = False

PROFILE_CONFIG = {
    "enabled": PROFILE,
    "storage": {"engine": "sqlite"},
    "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
    "ignore": ["^/static/.*"],
}

# Postgress Config
PSQL_HOST = os.getenv("DB_HOST", "localhost")
PSQL_DATABASE = os.getenv("DB_DATABASE", "postgres")
PSQL_USER = os.getenv("DB_USER", "postgres")
PSQL_PASSWORD = os.getenv("DB_PASSWORD", "password")
PSQL_PORT = os.getenv("DB_PORT", 5432)
SQLALCHEMY_DATABASE_URL = f"postgresql://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DATABASE}"

# MongoDB Config
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

CONNECT_PSQL = os.getenv("CONNECT_PSQL", "YES")
CONNECT_MONGO = os.getenv("CONNECT_MONGO")

DATABASE = {
    "SQL": {"SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL},
    "MONGO": {
        "HOST": MONGO_HOST,
        "USER": MONGO_USER,
        "PASSWORD": MONGO_PASSWORD,
        "PORT": MONGO_PORT,
        "DATABASE": MONGO_DATABASE,
        "AUTH_SOURCE": MONGO_AUTH_SOURCE,
    },
    "APP_CONFIG": {
        "CONNECT_PSQL": CONNECT_PSQL is not None,
        "CONNECT_MONGO": CONNECT_MONGO is not None,
    },
}

RESTX_MASK_SWAGGER = False
