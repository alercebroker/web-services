import json
from fastapi.encoders import jsonable_encoder
from ..models.object import Object


def object_parser(sql_response):
    for model in sql_response:
        model_dict = model.__dict__
        model_parsed = Object(**model_dict)

    return jsonable_encoder(model_parsed)


def loads_objects_list(objects):
    if objects is None:
        return None

    res = []
    for object in objects:
        object_json = json.loads(object)
        object_json = Object(**object_json)
        res.append(jsonable_encoder(object_json))

    return res
