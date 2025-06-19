
from core.repository.queries.objects import query_get_objects, query_object_by_id
from .parsers import (
    parse_params,
    parse_objects_list_output,
    parse_unique_object_query
)


def get_object_by_id(session_ms, oid, survey_id):

    object_model = query_object_by_id(session_ms, oid, survey_id)
    response = parse_unique_object_query(object_model)

    return response


def get_objects_list(session_ms, search_params):
    parsed_params = parse_params(search_params)

    result = query_get_objects(session_ms, search_params, parsed_params)
    result = parse_objects_list_output(result)

    return result


