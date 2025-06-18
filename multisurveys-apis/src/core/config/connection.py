import logging
import os
from contextlib import contextmanager
from typing import Generator

from db_plugins.db.sql._connection import PsqlDatabase
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

logger = logging.getLogger(__name__)


# user = os.getenv("PSQL_USER")
# pwd = os.getenv("PSQL_PASSWORD")
# host = os.getenv("PSQL_HOST")
# port = os.getenv("PSQL_PORT")
# db = os.getenv("PSQL_DATABASE")
# db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


db_config = {
    "USER": os.getenv("PSQL_USER"),
    "PASSWORD": os.getenv("PSQL_PASSWORD"),
    "DB_NAME": os.getenv("PSQL_DATABASE"),
    "HOST": os.getenv("PSQL_HOST"),
    "PORT": os.getenv("PSQL_PORT"),
    "SCHEMA": os.getenv("SCHEMA"),
}


def psql_entity():
    ms_entity_psql = PsqlDatabase(db_config)

    return ms_entity_psql


def connect() -> Engine:
    engine: Engine = create_engine(db_url, echo=False)
    return engine


def session_wrapper(engine: Engine):

    def _session() -> Generator[Session, None, None]:
        
        session_factory = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        session: Session = session_factory()
        try:
            yield session
        except Exception:
            logger.debug("Connecting databases")
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()

    return _session
