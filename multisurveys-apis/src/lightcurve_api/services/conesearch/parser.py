from typing import List
from db_plugins.db.sql.models import Object

from lightcurve_api.models.object import ApiObject
from core.idmapper.idmapper import decode_masterid
from numpy import int64


def parse_api_object(sql_object: Object) -> ApiObject:
    _, parsedOid = decode_masterid(int64(str(sql_object.oid)))
    return ApiObject(
        objectId=str(parsedOid),
        ra=sql_object.meanra,  # type: ignore
        dec=sql_object.meandec,  # type: ignore
    )


def parsesapi_objects(sql_objects: List[Object]) -> List[ApiObject]:
    return [parse_api_object(sql_object) for sql_object in sql_objects]
