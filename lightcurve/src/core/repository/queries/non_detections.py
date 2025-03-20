from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import (
    NonDetection,
)

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from ...exceptions import (
    DatabaseError,
)

from lightcurve_api.models.nondetection import NonDetection as NonDetectionModel
from lightcurve_api.parser.lightcurve_parser import _ztf_non_detection_to_multistream


# def _get_non_detections_sql(
#     session_factory: Callable[..., AbstractContextManager[Session]],
#     oid: str,
#     tid: str,
# ) -> list[NonDetectionModel]:
#     if tid == "atlas":
#         return []
#     try:
#         with session_factory() as session:
#             stmt = select(NonDetection, text("'ztf'")).where(
#                 NonDetection.oid == oid
#             )
#             result = session.execute(stmt)
#             result = [
#                 _ztf_non_detection_to_multistream(res[0].__dict__, tid=res[1])
#                 for res in result.all()
#             ]
#             return result
#     except Exception as e:
#         raise DatabaseError(e, database="PSQL")



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

# def _get_non_detections_sql(
#     session_factory: Callable[..., AbstractContextManager[Session]],
#     oid: str,
#     tid: str,
# ) -> list[NonDetectionModel]:
#     if tid == "atlas":
#         return []

#     result = _query_non_detections_sql(session_factory, oid, tid)
#     result = [
#         _ztf_non_detection_to_multistream(res[0].__dict__, tid=res[1])
#         for res in result
#     ]
#     return result
