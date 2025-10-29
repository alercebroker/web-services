from core.repository.queries.objects import (
    query_object_by_id
)

def get_object_by_id(session_ms, oid, lsst):
    results = query_object_by_id(session_ms,  oid, 'lsst')

    return oid