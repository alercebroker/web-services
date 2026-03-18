import json
from typing import List, cast
from db_plugins.db.sql.models import Object

from lightcurve_api.models.object import ApiObject
from core.idmapper.idmapper import decode_masterid
from numpy import int64

from ...models.lightcurve_item import BaseDetection, BaseForcedPhotometry, BaseNonDetection
from ...models.detections import LsstDetection, ztfDetection
from ...models.force_photometry import LsstForcedPhotometry, ZtfForcedPhotometry
from ...models.non_detections import ZtfNonDetections


def survey_id_map(sid: int) -> str:
    mapping = {
        0: "ztf",
        1: "lsst",
        2: "lsst_ss",
    }
    return mapping[sid]


def parse_api_object(sql_object: Object) -> ApiObject:
    objectId = sql_object.oid
    if survey_id_map(cast(int, sql_object.sid)) == "ztf":
        _, objectId = decode_masterid(int64(str(sql_object.oid)))
    return ApiObject(
        objectId=str(objectId),
        survey_id=survey_id_map(cast(int, sql_object.sid)),
        ra=sql_object.meanra,  # type: ignore
        dec=sql_object.meandec,  # type: ignore
    )


def parsesapi_objects(sql_objects: List[Object]) -> List[ApiObject]:
    return [parse_api_object(sql_object) for sql_object in sql_objects]


def parse_lightcurve_model_to_jsonstring(
        list_instances: list[BaseDetection] | list[BaseForcedPhotometry] | list[BaseNonDetection]
    ) -> str:
    """Parses a lightcurve model (e.g. list of detections) to a JSON string for caching."""

    list_of_dicts = [instance.model_dump() for instance in list_instances]
    return json.dumps(list_of_dicts)

def parse_jsonstring_to_lightcurve_model(
        json_string: str,
        model_class: BaseDetection | BaseForcedPhotometry | BaseNonDetection,
    ) -> list[BaseDetection] | list[BaseForcedPhotometry] | list[BaseNonDetection] :
    """Parses a JSON string back into a lightcurve model."""

    list_of_dicts = json.loads(json_string)
    return [model_class(**d) for d in list_of_dicts]  

class DetectionCacheUtil():
    key = "detections"
    models = {
        "ztf": ztfDetection,
        "lsst": LsstDetection,
    }

class ForcedPhotometryCacheUtil():
    key = "forced_photometry"
    models = {
        "ztf": ZtfForcedPhotometry,
        "lsst": LsstForcedPhotometry,
    }

class NonDetectionsCacheUtil():
    key = "non_detections"
    models = {
        "ztf": ZtfNonDetections,
        "lsst": BaseNonDetection,  # we currently don't have a separate non-detections model for lsst, so we use the base model
    }