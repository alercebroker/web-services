import pprint
from fastapi.encoders import jsonable_encoder
from core.repository.queries.objects import query_get_objects, query_object_by_id
from .parsers import (
    parse_params,
    parse_objects_list_output,
    parse_result_query
)


def get_object_by_id(session_ms, id):

    query_response = query_object_by_id(session_ms, id)

    response = parse_result_query(query_response)


    return response


def get_objects_list(session_ms, search_params):
    parsed_params = parse_params(search_params)

    result = query_get_objects(session_ms, search_params, parsed_params)
    result = parse_objects_list_output(result)

    return result
