from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.probability import get_probability_by_oid
from core.repository.queries.classifiers import get_all_classifiers
from src.core.idmapper.idmapper import encode_ids
from .parser import parse_grouped_probabilities, parse_probability, parse_classifiers
from src.probability_api.models.probability import ObjectProbability


def get_object_probability_model(
    oid: str, survey: str, session_factory: Callable[..., AbstractContextManager[Session]] | None = None
) -> ObjectProbability:
    """
    Create an ObjectProbability model instance.
    """

    master_id = encode_ids(survey, [oid])
    all_classifiers = get_classifiers(session_factory)

    return ObjectProbability(oid=int(master_id[0]), survey=survey, classifiers=all_classifiers)


def get_probability_for_frontend(
    object: ObjectProbability,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
) -> dict:
    probabilities = get_probability(object.oid, object.classifiers, session_factory=session_factory)

    parsed_probabilities = parse_grouped_probabilities(probabilities)

    return parsed_probabilities


def get_probability(
    oid,
    classifiers: dict,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
) -> dict:
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
