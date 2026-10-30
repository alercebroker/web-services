from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.probability import get_probability_by_oid
from core.idmapper.survey_mapper import get_survey_id
from core.repository.queries.classifiers import get_all_classifiers, get_classifier_by_name
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
    probabilities = get_probability(object.oid, object.classifiers, object.survey, session_factory=session_factory)

    parsed_probabilities = parse_grouped_probabilities(probabilities)

    return parsed_probabilities


def get_probability(
    oid,
    classifiers: dict,
    survey: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
) -> dict:
    classifier_id = None
    if len(classifiers) == 1:
        classifier_id = list(classifiers.keys())[0]

    result = get_probability_by_oid(oid, classifier_id, get_survey_id(survey), session_factory=session_factory)

    parsed_result = parse_probability(result, classifiers)
    return parsed_result


def get_classifier_id(
    classifier_name: str,
    survey: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> int | None:
    """The id of the survey's classifier with that name: the highest, its latest version. None if there is none.

    A name isn't unique across surveys (the same model for ZTF and LSST), so the survey comes first.
    """
    sid = get_survey_id(survey)
    ids = [
        row["classifier_id"] for row in get_classifier_by_name(classifier_name, session_factory) if row["tid"] == sid
    ]
    return max(ids, default=None)


def get_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
) -> dict[int, str]:
    result = get_all_classifiers(session_factory)

    parsed_result = parse_classifiers(result)
    return parsed_result
