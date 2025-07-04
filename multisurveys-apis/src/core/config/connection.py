import logging
import os

from db_plugins.db.sql._connection import PsqlDatabase

logger = logging.getLogger(__name__)

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
