from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.detections import get_all_unique_detections_sql
from core.repository.queries.non_detections import get_all_unique_non_detections_sql
from core.repository.queries.forced_photometry import get_unique_forced_photometry_sql
from .parsers import parse_sql_detection, parse_sql_non_detections, parse_forced_photometry
from .statements import convert_filters_non_detections_sql_alchemy


def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    
    result = get_all_unique_detections_sql(
        oid, survey_id, session_factory=session_factory
    )

    result = parse_sql_detection(result, survey_id)

    return result


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """Retrieves all unique non-detections from the databases for a given
    object in a given survey.
    """


    filters = convert_filters_non_detections_sql_alchemy(oid, survey_id)

    non_detections_result = get_all_unique_non_detections_sql(filters, session_factory)

    result_parsed = parse_sql_non_detections(non_detections_result, survey_id)


    return result_parsed


def get_forced_photometry(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """
    Retrieves the forced photometry from an object
    """

    forced_photometry = get_unique_forced_photometry_sql(
        oid, survey_id, session_factory
    )

    result_parsed = parse_forced_photometry(forced_photometry, survey_id)

    return result_parsed


def get_lightcurve(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    """
    Retrieves both unique detections and non detections for a given object in
    a given survey.
    """

    detections = get_detections(
        oid, survey_id, session_factory=session_factory
    )
    non_detections = get_non_detections(
        oid, survey_id, session_factory=session_factory
    )
    forced_photometry = get_forced_photometry(
        oid, survey_id, session_factory
    )


    return {
        "detections": detections,
        "non_detections": non_detections,
        "forced_photometry": forced_photometry,
    }
