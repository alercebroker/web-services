from src.aladin_api.models.object import RawObjectsRequest
from src.core.idmapper.idmapper import encode_ids
from ..services.aladin_parser import object_parser, loads_objects_list
from core.repository.queries.objects import query_common_object


def get_object_by_id(session_ms, oid, survey) -> dict:
    results = query_common_object(session_ms, oid, survey)

    response = object_parser(results)

    return response


def prepare_aladin_data(session_ms, raw_objects_request: RawObjectsRequest) -> tuple[list, dict]:
    encode_selected_oid = get_encode_oid(raw_objects_request.sid, raw_objects_request.selected_oid)
    selected_oid_data = get_object_by_id(session_ms=session_ms, oid=encode_selected_oid, survey="")

    objects_list = loads_objects_list(raw_objects_request.objects)
    selected_oid_data["oid"] = raw_objects_request.selected_oid

    return objects_list, selected_oid_data


def get_encode_oid(survey, oid) -> int:
    oid = encode_ids(survey, [oid])
    return int(oid[0])
