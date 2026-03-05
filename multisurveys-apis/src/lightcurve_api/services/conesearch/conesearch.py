from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, ContextManager, List, Tuple, cast

from numpy import int64
from sqlalchemy.orm import Session
from toolz.functoolz import pipe

import core.repository.queries.conesearch as queries
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.object import ApiObject
from lightcurve_api.services.conesearch.validation import (
    validate_coordinates_params,
    validate_oid_params,
)
from lightcurve_api.services.lightcurve_service import idmapper

from .parser import parsesapi_objects
from lightcurve_api.services import lightcurve_service


def conesearch_coordinates(
    ra: float,
    dec: float,
    radius: float,
    neighbors: int,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[ApiObject]:
    return cast(
        List[ApiObject],
        pipe(
            (ra, dec, radius, neighbors),
            validate_coordinates_params,
            queries.conesearch_coordinates(session_factory),
            parsesapi_objects,
        ),
    )


def conesearch_oid(
    oid: int64,
    radius: float,
    neighbors: int,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[ApiObject]:
    return cast(
        List[ApiObject],
        pipe(
            (oid, radius, neighbors),
            validate_oid_params,
            queries.dummy_conesearch_oid(session_factory),
            parsesapi_objects,
        ),
    )


def get_detections(
    session_factory: Callable[..., ContextManager[Session]],
    result: Lightcurve,
):
    def _get(objects: List[ApiObject]) -> Tuple[Lightcurve, dict]:
        object_ids_by_survey = defaultdict(lambda: [])
        for obj in objects:
            object_ids_by_survey[obj.survey_id].append(obj.objectId)
        for survey_id, object_ids in object_ids_by_survey.items():
            result.detections.extend(lightcurve_service.get_detections_by_list(object_ids, survey_id, session_factory))

        # now return result and the flattened list of object ids
        return result, object_ids_by_survey

    return _get


def get_non_detections(session_factory: Callable[..., ContextManager[Session]]):
    def _get(args: Tuple[Lightcurve, dict]) -> Tuple[Lightcurve, dict]:
        result, object_ids_by_survey = args

        for survey_id, object_ids in object_ids_by_survey.items():
            result.non_detections.extend(
                lightcurve_service.get_non_detections_by_list(object_ids, survey_id, session_factory)
            )

        return result, object_ids_by_survey

    return _get


def get_forced_photometry(session_factory: Callable[..., ContextManager[Session]]):
    def _get(args: Tuple[Lightcurve, dict]) -> Tuple[Lightcurve, dict]:
        result, object_ids_by_survey = args
        for survey_id, object_ids in object_ids_by_survey.items():
            raw_data = lightcurve_service.get_forced_photometry_by_list(object_ids, survey_id, session_factory)
            filtered_data = [obs for obs in raw_data if obs.psfFlux != 0.0]
            result.forced_photometry.extend(filtered_data)
        return result, object_ids_by_survey

    return _get


def conesearch_oid_lightcurve(
    oid: str,
    radius: float,
    neighbors: int,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
) -> Lightcurve:
    return cast(
        Lightcurve,
        pipe(
            idmapper.catalog_oid_to_masterid(survey_id, oid, True),
            lambda oid: conesearch_oid(oid, radius, neighbors, session_factory),
            get_lightcurve_async(
                session_factory,
                Lightcurve(detections=[], non_detections=[], forced_photometry=[]),
            ),
            lambda result: result[0],  # here we only care about result object, and discard the object ids dictionary
        ),
    )


def get_lightcurve_async(
    session_factory: Callable[..., ContextManager[Session]],
    result: Lightcurve,
):
    """
    This is a synchronous function thay run 3 sync funciontions in an asynchronous way.
    It mantains the functions intgerface for the get conesearch_oid_lightcurve pipe, but
    runs the get_detections, get_non_etections and get_forced_photometry queries with threads.
    """

    def _get(objects: List[ApiObject]) -> Tuple[Lightcurve, dict]:
        object_ids_by_survey = defaultdict(lambda: [])

        # THIS ASUME THAT ONLY 1 OBJECT IS RETURNED, TO BE ABLE TO THE THE LIGHTCURVE
        # WITH MULTIPLE OBJECTS REQUIRES MORE REFACTORS. ITS TOTALLY POSIBLE BUTH
        # WITH OTHER IMPLEMENTATION OF ASYNC CALLS
        oids = [objects[0].objectId]
        survey_id = objects[0].survey_id
        object_ids_by_survey[survey_id].append(oids)

        with ThreadPoolExecutor(max_workers=3) as executor:
            detections_executor = executor.submit(
                lightcurve_service.get_detections_by_list, oids, survey_id, session_factory
            )
            non_detections_executor = executor.submit(
                lightcurve_service.get_non_detections_by_list, oids, survey_id, session_factory
            )
            forced_photometry_executor = executor.submit(
                lightcurve_service.get_forced_photometry_by_list, oids, survey_id, session_factory
            )

            detections_result = detections_executor.result()
            non_detections_result = non_detections_executor.result()
            forced_photometry_result_raw = forced_photometry_executor.result()

        forced_photometry_result_filtered = [obs for obs in forced_photometry_result_raw if obs.psfFlux != 0.0]

        result.detections.extend(detections_result)
        result.non_detections.extend(non_detections_result)
        result.forced_photometry.extend(forced_photometry_result_filtered)

        return result, object_ids_by_survey

    return _get
