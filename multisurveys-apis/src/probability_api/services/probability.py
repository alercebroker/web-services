from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.probability import get_probability_by_oid
from core.repository.queries.classifiers import get_all_classifiers
from .parser import parse_probability, parse_classifiers


def get_probability(
    oid,
    classifiers: dict,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    classifier_id = None
    if len(classifiers) == 1:
        classifier_id = list(classifiers.keys())[0]

    result = get_probability_by_oid(oid, classifier_id, session_factory=session_factory)

    parsed_result = parse_probability(result, classifiers)
    return parsed_result


def get_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
) -> int | None:
    result = get_all_classifiers(session_factory)

    parsed_result = parse_classifiers(result)
    return parsed_result
