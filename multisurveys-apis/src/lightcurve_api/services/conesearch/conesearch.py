from collections import defaultdict
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
            queries.conesearch_oid(session_factory),
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
            result.forced_photometry.extend(
                lightcurve_service.get_forced_photometry_by_list(object_ids, survey_id, session_factory)
            )

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
            get_detections(session_factory, Lightcurve(detections=[], non_detections=[], forced_photometry=[])),
            get_non_detections(session_factory),
            get_forced_photometry(session_factory),
            lambda result: result[0],  # here we only care about result object, and discard the object ids dictionary
        ),
    )
