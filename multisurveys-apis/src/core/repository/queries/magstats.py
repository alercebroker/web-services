from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models_pipeline import LsstDiaObject, MagStat
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_magstats_by_oid(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    """
    Retrieves the magstats for a given object in a given survey.
    Args:
        oid: The object ID.
        session_factory: A factory function to create a database session.
            Defaults to None.
    """

    with session_factory() as session:
        if survey_id == "ztf":
            stmt = select(MagStat).where(MagStat.oid == oid)
        elif survey_id == "lsst":
            stmt = select(LsstDiaObject).where(LsstDiaObject.oid == oid)

        result = session.execute(stmt).all()

        return result
