import json

from typing import Callable, ContextManager, List, Tuple, cast

from sqlalchemy.orm import Session
from toolz import pipe

from core.config.cache import CacheEntity
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
from ..models.detections import LsstDetection
from ..models.force_photometry import LsstForcedPhotometry
from valkey import Valkey
from ..services.conesearch.parser import parse_lightcurve_model_to_jsonstring, parse_jsonstring_to_lightcurve_model, DetectionCacheUtil, ForcedPhotometryCacheUtil, NonDetectionsCacheUtil

def cache_query_wrapper(
        cache_util: DetectionCacheUtil | ForcedPhotometryCacheUtil | NonDetectionsCacheUtil,
    ):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_client: Valkey = CacheEntity()
            oid = args[0]
            survey_id = args[1]
            cache_key = f"{cache_util.key}:{survey_id}:{oid}"
            cached_result = cache_client.get(cache_key)

            if cached_result is not None:
                result_model = parse_jsonstring_to_lightcurve_model(cached_result, cache_util.models[survey_id])
                return result_model
            
            result = func(*args, **kwargs)
            result_parsed_json = parse_lightcurve_model_to_jsonstring(result)
            cache_client.set(cache_key, result_parsed_json)
            return result
        
        return wrapper
    
    return decorator

@cache_query_wrapper(DetectionCacheUtil)
def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    result = detection_repository.get_all_unique_detections_sql(oid, survey_id, session_factory=session_factory)

    result = parse_sql_detection((result, survey_id))

    return result

@cache_query_wrapper(DetectionCacheUtil)
def get_detections_by_list(
    oids: List[str],
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[BaseDetection]:
    result = cast(
        List[BaseDetection],
        pipe(
            (oids, survey_id),
            convert_oid_list_to_int,
            detection_repository.get_detections_by_list(session_factory),
            parse_sql_detection,
        ),
    )
    return result


def convert_oid_list_to_int(
    args: Tuple[List[int] | List[str], str],
) -> Tuple[List[int], str]:
    oid_list, survey_id = args

    return [idmapper.catalog_oid_to_masterid(survey_id, oid).item() for oid in oid_list], survey_id

@cache_query_wrapper(NonDetectionsCacheUtil)
def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    """Retrieves all unique non-detections from the databases for a given
    object in a given survey.
    """

    non_detections_result = non_detections_repository.get_all_unique_non_detections_sql(oid, survey_id, session_factory)

    result_parsed = parse_sql_non_detections((non_detections_result, survey_id))

    return result_parsed

@cache_query_wrapper(NonDetectionsCacheUtil)
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

@cache_query_wrapper(ForcedPhotometryCacheUtil)
def get_forced_photometry(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    """
    Retrieves the forced photometry from an object
    """

    forced_photometry = forced_photometry_repository.get_unique_forced_photometry_sql(oid, survey_id, session_factory)

    result_parsed = parse_forced_photometry((forced_photometry, survey_id))

    return result_parsed

@cache_query_wrapper(ForcedPhotometryCacheUtil)
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
