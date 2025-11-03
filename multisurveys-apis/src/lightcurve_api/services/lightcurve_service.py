from typing import Callable, ContextManager, List, Tuple, cast

from sqlalchemy.orm import Session
from toolz import pipe

from core.idmapper import idmapper
from core.repository.queries import detections as detection_repository
from core.repository.queries import non_detections as non_detections_repository
from core.repository.queries import (
    forced_photometry as forced_photometry_repository,
)
from lightcurve_api.models.lightcurve_item import (
    BaseDetection,
    BaseForcedPhotometry,
    BaseNonDetection,
)

from .parsers import (
    parse_forced_photometry,
    parse_sql_detection,
    parse_sql_non_detections,
)


def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    result = detection_repository.get_all_unique_detections_sql(
        oid, survey_id, session_factory=session_factory
    )

    result = parse_sql_detection((result, survey_id))

    return result


def get_detections_by_list(
    oids: List[str],
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[BaseDetection]:
    return cast(
        List[BaseDetection],
        pipe(
            (oids, survey_id),
            convert_oid_list_to_int,
            detection_repository.get_detections_by_list(session_factory),
            parse_sql_detection,
        ),
    )


def convert_oid_list_to_int(
    args: Tuple[List[int] | List[str], str],
) -> Tuple[List[int], str]:
    oid_list, survey_id = args

    return [
        idmapper.catalog_oid_to_masterid(survey_id, oid).item() for oid in oid_list
    ], survey_id


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    """Retrieves all unique non-detections from the databases for a given
    object in a given survey.
    """

    non_detections_result = non_detections_repository.get_all_unique_non_detections_sql(
        oid, survey_id, session_factory
    )

    result_parsed = parse_sql_non_detections((non_detections_result, survey_id))

    return result_parsed


def get_non_detections_by_list(
    oids: List[str],
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[BaseNonDetection]:
    return cast(
        List[BaseNonDetection],
        pipe(
            (oids, survey_id),
            convert_oid_list_to_int,
            non_detections_repository.get_non_detections_by_list(session_factory),
            parse_sql_non_detections,
        ),
    )


def get_forced_photometry(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    """
    Retrieves the forced photometry from an object
    """

    forced_photometry = forced_photometry_repository.get_unique_forced_photometry_sql(
        oid, survey_id, session_factory
    )

    result_parsed = parse_forced_photometry((forced_photometry, survey_id))

    return result_parsed


def get_forced_photometry_by_list(
    oids: List[str],
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[BaseForcedPhotometry]:
    return cast(
        List[BaseForcedPhotometry],
        pipe(
            (oids, survey_id),
            convert_oid_list_to_int,
            forced_photometry_repository.get_forced_photometry_by_list(session_factory),
            parse_forced_photometry,
        ),
    )


def get_lightcurve(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    """
    Retrieves both unique detections and non detections for a given object in
    a given survey.
    """

    detections = get_detections(oid, survey_id, session_factory=session_factory)
    non_detections = get_non_detections(oid, survey_id, session_factory=session_factory)
    forced_photometry = get_forced_photometry(oid, survey_id, session_factory)

    return {
        "detections": detections,
        "non_detections": non_detections,
        "forced_photometry": forced_photometry,
    }
