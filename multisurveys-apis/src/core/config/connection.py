import logging
import os
from db_plugins.db.sql._connection import PsqlDatabase
from sqlalchemy.engine import Engine, create_engine

logger = logging.getLogger(__name__)


user = os.getenv("PSQL_USER")
pwd = os.getenv("PSQL_PASSWORD")
host = os.getenv("PSQL_HOST")
port = os.getenv("PSQL_PORT")
db = os.getenv("PSQL_DATABASE")
db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


db_config = {
    "USER": os.getenv("PSQL_USER"),
    "PASSWORD": os.getenv("PSQL_PASSWORD"),
    "DB_NAME": os.getenv("PSQL_DATABASE"),
    "HOST": os.getenv("PSQL_HOST"),
    "PORT": os.getenv("PSQL_PORT"),
    "SCHEMA": os.getenv("SCHEMA"),
}


def psql_entity(engine):
    ms_entity_psql = PsqlDatabase(db_config, engine)

    return ms_entity_psql


def connect() -> Engine:
    schema = db_config.get("SCHEMA", None)

    engine: Engine = create_engine(
        db_url,
        echo=False,
        connect_args={"options": "-csearch_path={}".format(schema)},
    )
    return engine
