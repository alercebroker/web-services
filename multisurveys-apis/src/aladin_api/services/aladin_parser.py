import json
from fastapi.encoders import jsonable_encoder
from ..models.object import Object


def object_parser(sql_response):
    for model in sql_response:
        model_dict = model.__dict__
        model_dict["oid"] = str(model_dict["oid"])
        model_parsed = Object(**model_dict)

    return jsonable_encoder(model_parsed)

def loads_objects_list(objects):
    if objects is None:
        return None

    json_string = (objects
        .replace("'", '"')
        .replace("None", "null")
        .replace("False", "false")
        .replace("True", "true")
    )
    objects_json = json.loads(json_string)

    res = []
    for object in objects_json:
        object["oid"] = str(object["oid"])
        object_model = Object(**object)
        return_model = object_model.model_dump()
        res.append(return_model)

    return res