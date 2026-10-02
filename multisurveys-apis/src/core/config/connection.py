import logging
import os
import threading

from db_plugins.db.sql._connection_pipeline import PsqlDatabase, get_db_url
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)


def build_engine(db_config: dict):
    """
    Engine for the APIs' read-only sessions.

    AUTOCOMMIT drops the BEGIN and ROLLBACK around every read, so a query costs one round trip to the database
    instead of three, and its PgBouncer connection is released as soon as the query ends. This lives here and
    not in db-plugins, because the pipeline also uses that library and needs its multi-statement writes atomic.

    Passing our own engine skips db-plugins' search_path setup, so it is repeated here whenever SCHEMA is set
    (local runs and tests). Prod doesn't set SCHEMA: it relies on each API user's search_path.
    """
    connect_args = {}
    if db_config["SCHEMA"]:
        connect_args["options"] = f"-csearch_path={db_config['SCHEMA']}"
    return create_engine(
        get_db_url(db_config),
        echo=False,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
        connect_args=connect_args,
    )


class ApiDatabase:
    """Singleton wrapper for PsqlDatabase"""

    _instance = None
    # Route handlers run in threads, so two first requests could otherwise each build an instance.
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    db_config = {
                        "USER": os.getenv("PSQL_USER"),
                        "PASSWORD": os.getenv("PSQL_PASSWORD"),
                        "DB_NAME": os.getenv("PSQL_DATABASE"),
                        "HOST": os.getenv("PSQL_HOST"),
                        "PORT": os.getenv("PSQL_PORT"),
                        "SCHEMA": os.getenv("SCHEMA"),
                    }
                    cls._instance = PsqlDatabase(db_config, engine=build_engine(db_config))
        return cls._instance


def psql_entity():
    return ApiDatabase()
