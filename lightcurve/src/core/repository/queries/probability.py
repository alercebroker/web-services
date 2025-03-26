from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models import (
    Probability,
)

from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session
from core.exceptions import DatabaseError

def _query_probabilities_sql(
    oid: str, 
    session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Probability).where(Probability.oid == oid)
            result = session.execute(stmt)
            prob_list = result.all()
            return prob_list
    except Exception as e:
        raise DatabaseError(e, database="PSQL")