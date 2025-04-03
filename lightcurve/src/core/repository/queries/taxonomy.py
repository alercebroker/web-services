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
    

def _query_taxonomie_class(
        session_factory: Callable[..., AbstractContextManager[Session]],
        classifier_name: str,
        classifier_version: str
    ):
    with session_factory() as session:
        classifier = (
            session.query(Taxonomy)
            .filter(Taxonomy.classifier_name == classifier_name)
            .filter(
                Taxonomy.classifier_version == classifier_version
            )
            .one_or_none()
        )
        if classifier is not None:
            classes = [{"name": c} for c in classifier.classes]
            return classes
        else:
           raise ValueError(f"No taxonomy found for classifier {classifier_name} version {classifier_version}")
