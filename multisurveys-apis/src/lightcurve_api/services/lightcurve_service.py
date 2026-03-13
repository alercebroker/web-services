import json

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
from ..models.detections import LsstDetection
from ..models.force_photometry import LsstForcedPhotometry

import valkey

VALKEY_HOST = "localhost" #os.getenv("VALKEY_HOST")
VALKEY_PORT = 6379 #os.getenv("VALKEY_PORT")

def get_glide_client():
    # TODO: we should not be creating a new client for every request, 
    # but this is a temporary solution until we have a better way to manage the client lifecycle
    print("creating cache client")
    client = valkey.Valkey(host=VALKEY_HOST, port=VALKEY_PORT)
    response = client.ping()
    print(f"Successfully connected to Glide Valkey at {VALKEY_HOST}:{VALKEY_PORT} - Ping response: {response}")
    return client


def get_cache_value(key: str):
    client = get_glide_client()
    value = client.get(key)
    print(f"\t --- \t -- Retrieved cache value for key: {key} \n value: {value}")
    return value

def set_cache_value(key: str, value):
    client = get_glide_client()
    client.set(key, str(value))

def cache_query_wrapper(cache_key_prefix):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"HERE ARE THE ARGS:\n {args} \n {kwargs}")
            oid = args[0]
            survey_id = args[1]
            cache_key = f"{cache_key_prefix}:{oid}:{survey_id}"
            print(f"Checking cache for key: {cache_key}")
            cached_result = get_cache_value(cache_key)
            #cached_result = None # disable cache for now
            if cached_result is not None:
                print(f"Cache hit for key: {cache_key} \n with result: {cached_result}")
                cache_loaded = json.loads(cached_result)
                print(f"\n\n ------ \n -- \nCache loaded\n loaded value: {cache_loaded}")
                if cache_key_prefix == "detections":
                    result_model = [LsstDetection(**r) for r in cache_loaded]
                else:
                    result_model = [LsstForcedPhotometry(**r) for r in cache_loaded]
                return result_model
            
            print("Cache miss, executing query...")
            result = func(*args, **kwargs)
            print(f"Query result: {result}")
            result_parsed = [r.model_dump() for r in result]
            result_parsed_json = json.dumps(result_parsed)
            print(f"\n---\n parsed result: {result_parsed_json}\n---\n")
            # if cache_key_prefix == "detections":
            #     result_model = [LsstDetection(**json.loads(r)) for r in result_parsed]
            # else:
            #     result_model = [LsstForcedPhotometry(**json.loads(r)) for r in result_parsed]
            # print(f"\n--    --\n result model: {result_model}\n--    --\n")
            print(f"Setting cache for key: {cache_key} \n with result: {result_parsed_json}")
            set_cache_value(cache_key, result_parsed_json)
            return result
        
        return wrapper
    
    return decorator

@cache_query_wrapper("detections")
def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    result = detection_repository.get_all_unique_detections_sql(oid, survey_id, session_factory=session_factory)

    result = parse_sql_detection((result, survey_id))

    return result

@cache_query_wrapper("detections")
def get_detections_by_list(
    oids: List[str],
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[BaseDetection]:
    print(f"\t -- \tGetting detections for OIDs: {oids} and survey_id: {survey_id}")
    result = cast(
        List[BaseDetection],
        pipe(
            (oids, survey_id),
            convert_oid_list_to_int,
            detection_repository.get_detections_by_list(session_factory),
            parse_sql_detection,
        ),
    )
    print(f"\t-- \tRetrieved {len(result)} detections")
    return result


def convert_oid_list_to_int(
    args: Tuple[List[int] | List[str], str],
) -> Tuple[List[int], str]:
    oid_list, survey_id = args

    return [idmapper.catalog_oid_to_masterid(survey_id, oid).item() for oid in oid_list], survey_id

@cache_query_wrapper("non_detections")
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

@cache_query_wrapper("non_detections")
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

@cache_query_wrapper("forced_photometry")
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

@cache_query_wrapper("forced_photometry")
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
