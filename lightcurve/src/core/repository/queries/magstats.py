from contextlib import AbstractContextManager
from typing import Callable
from db_plugins.db.sql.models import (
    MagStats
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...exceptions import (
    DatabaseError,
    ObjectNotFound,

)


def _query_sql_mag_stats(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
):
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(MagStats).where(MagStats.oid == oid)
            result = session.execute(stmt)
            first = result.all()
            
            return first
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")