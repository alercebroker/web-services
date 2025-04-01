from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import (
    NonDetection,
)

from sqlalchemy import select, text, asc, func, select
from sqlalchemy.orm import Session

from core.exceptions import DatabaseError, ObjectNotFound

from lightcurve_api.models.nondetection import NonDetection as NonDetectionModel
from lightcurve_api.parser.lightcurve_parser import _ztf_non_detection_to_multistream


def _query_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
):
    try:
        with session_factory() as session:
            stmt = select(NonDetection, text("'ztf'")).where(
                NonDetection.oid == oid
            )
            result = session.execute(stmt).all()
            return result
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    


def _query_count_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
):
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(NonDetection)
                .where(NonDetection.oid == oid)
            )
            result = session.execute(stmt)
            count = result.all()[0]
            if count is None:
                raise ObjectNotFound(oid)
            return count[0]
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
