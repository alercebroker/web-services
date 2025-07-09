from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import MagStat
from sqlalchemy.orm import Session
from sqlalchemy import select

def get_magstats_by_oid(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """
    Retrieves the magstats for a given object in a given survey.
    Args:
        oid (str): The object ID.
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.
    """

    with session_factory() as session:
        stmt = (
            select(MagStat)
            .where(MagStat.oid == oid)
        )

        result = session.execute(stmt).all()

        return result
