from contextlib import contextmanager
import logging
import os
from typing import Generator
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.engine import Engine, create_engine


logger = logging.getLogger(__name__)


user = os.getenv("PSQL_USER")
pwd = os.getenv("PSQL_PASSWORD")
host = os.getenv("PSQL_HOST")
port = os.getenv("PSQL_PORT")
db = os.getenv("PSQL_DATABASE")
db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


def connect() -> Engine:
    engine: Engine = create_engine(db_url, echo=False)
    return engine


def session_wrapper(engine: Engine):
    @contextmanager
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
