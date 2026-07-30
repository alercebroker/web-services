import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)


user = os.getenv("PSQL_USER")
pwd = os.getenv("PSQL_PASSWORD")
host = os.getenv("PSQL_HOST")
port = os.getenv("PSQL_PORT")
db = os.getenv("PSQL_DATABASE")
db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


def connect() -> Engine:
    # NullPool: pgbouncer already does transaction pooling in front of
    # Postgres, so an app-side pool would double-pool. This is not "a new
    # connection per request per Postgres" -- it means no *second* pool.
    #
    # AUTOCOMMIT: Postgres is on-prem in Chile, ~134 ms from the cluster, and
    # psycopg2's implicit BEGIN and the pool's reset-on-return ROLLBACK are
    # each a full round trip -- 3 per read where the query needs 1. These
    # sub-apps are read-only (no INSERT/UPDATE/DELETE, no FOR UPDATE, no temp
    # tables, no server-side cursors) and every service call already opens its
    # own session, so per-statement visibility is what they get today anyway.
    # Measured: -260 ms per read, -1308 ms over the 5 reads of htmx/lightcurve.
    engine: Engine = create_engine(
        db_url, echo=False, poolclass=NullPool, isolation_level="AUTOCOMMIT"
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
