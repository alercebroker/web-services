from ..services.aladin_parser import object_parser
from core.repository.queries.objects import (
    query_object_by_id
)

def get_object_by_id(session_ms, oid, lsst):
    results = query_object_by_id(session_ms,  oid, 'lsst')

    response = object_parser(results)

    return response
