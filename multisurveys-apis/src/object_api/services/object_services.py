import pprint
from fastapi.encoders import jsonable_encoder
from core.repository.queries.objects import query_get_objects, query_object_by_id
from .parsers import (
    parse_params,
    parse_objects_list_output,
)


def get_object_by_id(session_ms, id):

    object_entity, ztf_object = query_object_by_id(session_ms, id)
    result = jsonable_encoder(ztf_object, sqlalchemy_safe=True)

    return result


def get_objects_list(session_ms, search_params):
    parsed_params = parse_params(search_params)

    result = query_get_objects(session_ms, search_params, parsed_params)
    result = parse_objects_list_output(result)

    return result


