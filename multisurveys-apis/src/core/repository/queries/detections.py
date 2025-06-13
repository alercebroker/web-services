from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Object, ZtfDetection, Detection
from sqlalchemy.orm import Session
from sqlalchemy import select, text


def get_all_unique_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:
        stmt = build_statement(survey_id, oid)

        return session.execute(stmt).all()

    

def build_statement(survey_id, oid):


    if survey_id == "ztf":
        stmt = (
            select(ZtfDetection)
            .where(ZtfDetection.oid == oid)
            .limit(10)
        )
    elif survey_id == "lsst":
        pass
    else:
        stmt = text("")

    return stmt