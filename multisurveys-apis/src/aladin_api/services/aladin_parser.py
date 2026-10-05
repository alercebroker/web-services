import json
from fastapi.encoders import jsonable_encoder
from ..models.object import Object


def object_parser(sql_response) -> dict:
    parsed_object = Object.model_validate(sql_response[0], from_attributes=True)

    return jsonable_encoder(parsed_object)


def loads_objects_list(objects) -> list:
    if _object_is_empty(objects):
        return []

    objects_json = _parse_json_string(objects)

    res = []
    for object in objects_json:
        object["oid"] = str(object["oid"])
        object_model = Object(**object)
        return_model = object_model.model_dump()
        res.append(return_model)

    return res


def _parse_json_string(json_string):
    json_parsed = (
        json_string.replace("'", '"').replace("None", "null").replace("False", "false").replace("True", "true")
    )

    return json.loads(json_parsed)


def _object_is_empty(objects):
    if objects is None or objects == "":
        return True
