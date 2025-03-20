from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import (
    Detection,
)

from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from ...exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    ParseError,
    SurveyIdError,
)

from lightcurve_api.models.detection import Detection as DetectionModel
from lightcurve_api.parser.lightcurve_parser import _parse_sql_detection


# def _get_detections_sql(
#     session_factory: Callable[..., AbstractContextManager[Session]],
#     oid: str,
#     tid: str,
# ) -> list[DetectionModel]:
#     if tid == "atlas":
#         return []
#     result = list(_query_detections_sql(session_factory, oid))
#     result = _parse_sql_detection(result)
#     return result


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
