from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import (
    Detection,
)

from sqlalchemy import Row, select, text, asc
from sqlalchemy.orm import Session

from ...exceptions import (
    DatabaseError,
    ObjectNotFound,
)


def _query_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
) -> Sequence[Row[Tuple[Detection, Any]]]:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Detection, text("'ztf'")).filter(
                Detection.oid == oid
            )
            return session.execute(stmt).all()
    except Exception as e:
        raise DatabaseError(e, database="PSQL")


def _query_first_det_candid_sql(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> str:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = (
                select(Detection)
                .where(Detection.oid == oid)
                .where(Detection.has_stamp == True)
                .order_by(asc(Detection.mjd))
            )
            result = session.execute(stmt)
            first = result.first()

            if first is None:
                raise ObjectNotFound(oid)
            
            return first

    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")