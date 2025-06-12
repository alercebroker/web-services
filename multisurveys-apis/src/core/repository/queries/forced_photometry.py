from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import ZtfForcedPhotometry, ForcedPhotometry, Object
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_unique_forced_photometry_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:

        stmt = build_query(oid, survey_id)

        result = session.execute(stmt).all()
        
        return result


def build_query(oid, survey_id):

    stmt = ""

    if survey_id == "ztf":
        stmt = (
            select(ZtfForcedPhotometry)
            .where(ZtfForcedPhotometry.oid == oid)
        )


    return stmt