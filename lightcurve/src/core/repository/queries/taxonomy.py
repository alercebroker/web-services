from contextlib import AbstractContextManager
from typing import Callable
from db_plugins.db.sql.models import (Taxonomy)
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.exceptions import DatabaseError


def _query_taxonomies_sql(
    session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Taxonomy)
            result = session.execute(stmt)
            taxonomy_list = result.all()
            
            return taxonomy_list
        
    except Exception as e:
        raise DatabaseError(e, database="PSQL")