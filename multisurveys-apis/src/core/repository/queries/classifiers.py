from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import classifier_ms, Taxonomy_ms
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_classifier_by_name(
    classifier_name: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """
    Retrieves a classifier by its name.

    Args:
        classifier_name (str): The name of the classifier.
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.

    Returns:
        list: List of classifiers matching the given name.
    """
    with session_factory() as session:
        stmt = (
            select(classifier_ms, Taxonomy_ms)
            .join(
                Taxonomy_ms,
                classifier_ms.classifier_id == Taxonomy_ms.classifier_id,
            )
            .where(classifier_ms.classifier_name == classifier_name)
            .order_by(Taxonomy_ms.order.asc())
        )
        result = session.execute(stmt).all()
        return result


def get_all_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """
    Retrieves all classifiers.

    Args:
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.

    Returns:
        list: List of all classifiers.
    """
    with session_factory() as session:
        stmt = (
            select(classifier_ms, Taxonomy_ms)
            .join(
                Taxonomy_ms,
                classifier_ms.classifier_id == Taxonomy_ms.classifier_id,
            )
            .order_by(
                classifier_ms.classifier_name.asc(), Taxonomy_ms.order.asc()
            )
        )
        result = session.execute(stmt)
        result = result.all()
        return result
