import logging
import os

from db_plugins.db.sql._connection import PsqlDatabase

logger = logging.getLogger(__name__)


class ApiDatabase:
    """Singleton wrapper for PsqlDatabase"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            db_config = {
                "USER": os.getenv("PSQL_USER"),
                "PASSWORD": os.getenv("PSQL_PASSWORD"),
                "DB_NAME": os.getenv("PSQL_DATABASE"),
                "HOST": os.getenv("PSQL_HOST"),
                "PORT": os.getenv("PSQL_PORT"),
                "SCHEMA": os.getenv("SCHEMA"),
            }
            cls._instance = PsqlDatabase(db_config)
        return cls._instance


def psql_entity():
    return ApiDatabase()
