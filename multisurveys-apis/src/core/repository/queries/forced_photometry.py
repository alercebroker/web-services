from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import ZtfForcedPhotometry, LsstForcedPhotometry, ForcedPhotometry
from sqlalchemy.orm import Session
from sqlalchemy import select, and_


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
        .join(
            ForcedPhotometry, 
            and_(
                model_id.oid==ForcedPhotometry.oid,
                model_id.measurement_id==ForcedPhotometry.measurement_id
            )
        )
        .where(model_id.oid == oid)
        .limit(10)
    )


    return stmt