
from contextlib import AbstractContextManager
from typing import Callable
from db_plugins.db.sql.models import (
    Object,
)

from sqlalchemy import select
from sqlalchemy.orm import Session


from ...exceptions import (
    DatabaseError,
    ObjectNotFound,

)


def query_psql_object(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
):
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Object).where(Object.oid == oid)
            result = session.execute(stmt)
            first = result.first()
            if first is None:
                raise ObjectNotFound(oid)
            return first[0]
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")