from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import NonDetection, LsstNonDetection
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_all_unique_non_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:
        if survey_id == "lsst":
            stmt = build_statement(LsstNonDetection, oid)
        else:
            stmt = build_statement(NonDetection, oid)

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
