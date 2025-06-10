from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Object, ZtfDetection, Detection
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_all_unique_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:
        stmt = build_all_unique_detections_statement(survey_id, oid)

        return session.execute(stmt).all()
    

def build_all_unique_detections_statement(survey_id, oid):

    stmt = (
        select(Object)
    )

    if survey_id == "ztf":
        stmt = (
            stmt.add_columns(ZtfDetection)
            .join(ZtfDetection, ZtfDetection.oid == Object.oid)
            .limit(10)
        )

    if survey_id == "lsst":
        stmt = (
            stmt.add_columns(Detection)
            .join(Detection, Detection.oid == Object.oid)
        )

    stmt = (stmt.where(Object.oid == oid))

    return stmt