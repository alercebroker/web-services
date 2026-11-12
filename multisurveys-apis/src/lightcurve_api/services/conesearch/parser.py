from typing import List, cast
from db_plugins.db.sql.models_pipeline import Object

from lightcurve_api.models.object import ApiObject
from core.idmapper.idmapper import decode_masterid
from core.idmapper.survey_mapper import get_survey_name
from numpy import int64


def parse_api_object(sql_object: Object) -> ApiObject:
    objectId = sql_object.oid
    survey = get_survey_name(cast(int, sql_object.sid))
    if survey == "ztf":
        _, objectId = decode_masterid(int64(str(sql_object.oid)))
    return ApiObject(
        objectId=str(objectId),
        survey_id=survey,
        ra=sql_object.meanra,  # type: ignore
        dec=sql_object.meandec,  # type: ignore
    )


def parsesapi_objects(sql_objects: List[Object]) -> List[ApiObject]:
    return [parse_api_object(sql_object) for sql_object in sql_objects]
