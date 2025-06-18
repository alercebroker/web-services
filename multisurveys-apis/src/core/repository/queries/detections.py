from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Object, ZtfDetection, Detection, LsstDetection
from sqlalchemy.orm import Session
from sqlalchemy import select, text, and_


def get_all_unique_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:

        if survey_id == "ztf":
            stmt = build_statement(ZtfDetection, oid)
        elif survey_id == "lsst":
            stmt = build_statement(LsstDetection, oid)
        else:
            stmt = text('')

        return session.execute(stmt).all()

    

def build_statement(model_id, oid):

    stmt = (
        select(model_id, Detection)
        .join(
            Detection, and_(
            Detection.oid == model_id.oid,
            Detection.measurement_id == model_id.measurement_id
        ))
        .where(model_id.oid == oid)
        .limit(10)
    )

    return stmt