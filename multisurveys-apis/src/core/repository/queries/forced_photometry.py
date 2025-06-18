from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import ZtfForcedPhotometry, LsstForcedPhotometry, ForcedPhotometry, Object
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_unique_forced_photometry_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:


        if survey_id == "ztf":
            stmt = build_query(ZtfForcedPhotometry, oid)
        if survey_id == "lsst":
            stmt = build_query(LsstForcedPhotometry, oid)

        result = session.execute(stmt).all()
        
        return result


def build_query(model_id, oid):

    stmt = (
        select(model_id, ForcedPhotometry)
        .join(model_id, model_id.oid==ForcedPhotometry.oid)
        .where(model_id.oid == oid)
        .limit(10)
    )


    return stmt