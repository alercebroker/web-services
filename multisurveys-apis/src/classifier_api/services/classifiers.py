from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.classifiers import (
    get_all_classifiers as db_get_all_classifiers,
    get_classifier_by_name as db_get_classifier_by_name,
)
from ..models.classifiers import Classifiers
from .parsers import parse_classifiers


def get_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> list[Classifiers]:
    """Retrieves all classifiers from the database

    Args:
        session_factory (Callable[..., AbstractContextManager[Session]]): A factory function to create a database session.

    Returns:
        list[Classifiers]: One per classifier id, with its classes.
    """

    result = db_get_all_classifiers(session_factory)
    return parse_classifiers(result)


def get_classifier_by_name(
    classifier_name: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> list[Classifiers]:
    """
    Retrieves a classifier by its name.

    Args:
        classifier_name (str): The name of the classifier.
        session_factory (Callable[..., AbstractContextManager[Session]]): A factory function to create a database session.

    Returns:
        list[Classifiers]: The classifiers with that name, one per classifier id, with their classes.
    """

    result = db_get_classifier_by_name(classifier_name, session_factory)
    return parse_classifiers(result)
