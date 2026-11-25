import logging

from aladin_api.models.object import RawObjectsRequest
from core.idmapper.idmapper import encode_ids
from ..services.aladin_parser import object_parser, loads_objects_list
from core.repository.queries import association as association_repository
from core.repository.queries.objects import query_common_object
from lightcurve_api.services.group_service import association_enabled, display_oid

logger = logging.getLogger(__name__)


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

    Named by their survey's own id (the ZTF name, the LSST number). Empty without association data or a group;
    the association tables are still a test schema, so a failure only leaves them out of the panel.
    """
    if not association_enabled():
        return []
    try:
        group = association_repository.get_object_group(session_ms, oid, sid)
        if group is None:
            return []
        members = [m for m in association_repository.get_group_members(session_ms, group.group_id) if m != (oid, sid)]
        positions = association_repository.get_object_stats(session_ms, members)
    except Exception:
        logger.warning("Could not read the group of %s (sid %s)", oid, sid, exc_info=True)
        return []
    return [
        {
            "oid": display_oid(m_oid, m_sid),
            "sid": m_sid,
            "meanra": row.meanra,
            "meandec": row.meandec,
            "associated": True,
        }
        for (m_oid, m_sid), row in positions.items()
    ]


def get_encode_oid(survey, oid) -> int:
    oid = encode_ids(survey, [oid])
    return int(oid[0])
