from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.classifiers import (
    get_all_classifiers as db_get_all_classifiers,
    get_classifier_by_name as db_get_classifier_by_name,
)
from .parsers import parse_classifiers


def get_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    """Retrieves all classifiers from the database

    Args:
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.

    Returns:
        list: List of all classifiers.
    """

    result = db_get_all_classifiers(session_factory)
    return parse_classifiers(result)


def get_classifier_by_name(
    classifier_name: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    """
    Retrieves a classifier by its name.

    Args:
        classifier_name (str): The name of the classifier.
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.

    Returns:
        list: List of classifiers matching the given name.
    """

    result = db_get_classifier_by_name(classifier_name, session_factory)
    return parse_classifiers(result)
