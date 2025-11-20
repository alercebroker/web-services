from ..services.aladin_parser import object_parser
from core.repository.queries.objects import query_common_object


def get_object_by_id(session_ms, oid, survey):
    results = query_common_object(session_ms, oid, survey)

    response = object_parser(results)

    return response
