from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.detections import get_all_unique_detections_sql
from core.repository.queries.non_detections import get_all_unique_non_detections_sql
from .parsers import parse_sql_detection, parse_sql_non_detecions_to_multistream
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

    result = parse_sql_detection(result)

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

    result_parsed = parse_sql_non_detecions_to_multistream(non_detections_result)

    return result_parsed




