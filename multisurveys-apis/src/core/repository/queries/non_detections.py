from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import ZtfNonDetection
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_all_unique_non_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
):
    with session_factory() as session:
        if survey_id == "lsst":
            print("LSST non-detections not implemented yet")
            
            return []
        else:
            stmt = build_statement(ZtfNonDetection, oid)

            result = session.execute(stmt).all()

            return result


def build_statement(model_id, oid):
    stmt = (
        select(model_id)
        .where(model_id.oid == oid)
        .order_by(model_id.mjd.desc())
        .limit(10)
    )

    return stmt
