from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import NonDetection, Object, LsstNonDetection
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_all_unique_non_detections_sql(
    filters: dict,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:

        stmt = build_statement(filters, survey_id)

        result = session.execute(stmt).all()

        return result
    
def build_statement(filters, survey_id):

    if survey_id == "ztf":
        stmt = (
            select(NonDetection)
            .where(*filters.values())
            .order_by(NonDetection.mjd.desc())
            .limit(10)
        )
    elif survey_id == "lsst":
        stmt = (
            select(LsstNonDetection)
            .where(*filters.values())
            .order_by(LsstNonDetection.mjd.desc())
            .limit(10)
        )
    
    return stmt