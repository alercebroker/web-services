from ..models.object import Object


def parse_object(raw_object) -> Object:
    return Object.model_validate(raw_object, from_attributes=True)
