import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

logger = logging.getLogger(__name__)


alerts_user = os.getenv("ALERTS_USER")
alerts_pwd = os.getenv("ALERTS_PASSWORD")
alerts_host = os.getenv("ALERTS_HOST")
alerts_port = os.getenv("ALERTS_PORT")
alerts_db = os.getenv("ALERTS_DATABASE")
alerts_db_url = (
    f"postgresql://{alerts_user}:{alerts_pwd}@{alerts_host}:{alerts_port}/{alerts_db}"
)

scores_user = os.getenv("SCORES_USER")
scores_pwd = os.getenv("SCORES_PASSWORD")
scores_host = os.getenv("SCORES_HOST")
scores_port = os.getenv("SCORES_PORT")
scores_db = os.getenv("PSQL_DATABASE")
scores_schema = os.getenv("SCORES_SCHEMA")
scores_db_url = (
    f"postgresql://{scores_user}:{scores_pwd}@{scores_host}:{scores_port}/{scores_db}"
)


def connect_alerts() -> Engine:
    engine: Engine = create_engine(alerts_db_url, echo=False)
    return engine


def connect_scores() -> Engine:
    engine: Engine = create_engine(
        scores_db_url,
        echo=False,
        connect_args={"options": "-csearch_path={}".format(scores_schema)},
    )
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
