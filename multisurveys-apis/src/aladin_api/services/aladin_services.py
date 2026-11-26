from aladin_api.models.object import RawObjectsRequest
from core.idmapper.idmapper import encode_ids, public_oid
from ..services.aladin_parser import object_parser, loads_objects_list
from core.association import association_enabled, safe_lookup
from core.idmapper.survey_mapper import get_survey_name
from core.repository.queries import association as association_repository
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

    group = get_group_objects(session_ms, encode_selected_oid, selected_oid_data["sid"])
    in_group = {obj["oid"] for obj in group}
    objects_list = [obj for obj in objects_list if obj["oid"] not in in_group] + group

    return objects_list, selected_oid_data


def get_group_objects(session_ms, oid: int, sid: int) -> list[dict]:
    """The other members of the object's association group, at their mean position, marked ``associated``.

    Named by their survey's own id (the ZTF name, the LSST number). Empty without association data, a group, or
    when the lookup fails.
    """
    if not association_enabled():
        return []
    rows = safe_lookup(
        lambda: association_repository.get_counterpart_rows(session_ms, [(oid, sid)]),
        [],
        f"the group of {oid} (sid {sid})",
    )
    return [
        {
            "oid": public_oid(get_survey_name(row.sid), row.oid),
            "sid": row.sid,
            "meanra": row.meanra,
            "meandec": row.meandec,
            "associated": True,
        }
        for row in rows
        if row.meanra is not None
    ]


def get_encode_oid(survey, oid) -> int:
    oid = encode_ids(survey, [oid])
    return int(oid[0])
