from typing import List, cast
from db_plugins.db.sql.models import Object

from lightcurve_api.models.object import ApiObject
from core.idmapper.idmapper import decode_masterid
from numpy import int64


def survey_id_map(sid: int) -> str:
    return "ztf" if sid == 1 else "lsst"


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
