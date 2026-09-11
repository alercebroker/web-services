from sqlalchemy.orm import Session
from crossmatch_api.get_crossmatch_data import get_alerce_data
from core.idmapper.idmapper import encode_ids
from core.repository.queries.objects import (
    query_object_by_id,
)
from ..models.object import Object, ObjectInformation
from .parsers import parse_object


def get_cross_data(object_details: ObjectInformation, session: Session):

    object = get_object_data(object_details, session)
    cross = get_alerce_data(object.meanra, object.meandec, 20)


    return cross


def get_cross_for_frontend(object_details: ObjectInformation, session: Session):
    cross = get_cross_data(object_details, session)
    cross_keys = get_keys(cross)


    return cross, cross_keys



def get_object_data(object_details: ObjectInformation, session: Session) -> Object:
    master_oid = encode_ids(object_details.survey, [object_details.oid])[0]

    object_ztf, object = query_object_by_id(session, int(master_oid), object_details.survey)
    object = parse_object(object)


    return object


def get_keys(data) -> list:
    """
    Extract the top-level key from each dictionary in a list of single-key dictionaries.

    Expects `data` to be a list where each element is a dict containing exactly
    one key-value pair, e.g.:

        [{'name1': {...}}, {'name2': {...}}, {'name3': {...}}]

    Returns a list of those keys in order, e.g.:

        ['name1', 'name2', 'name3']

    Uses next(iter(d)) on each dict to grab its single key without building
    a full list of keys first.
    """

    response = []
    for i in range(len(data)):
        response.append(next(iter(data[i].keys())))


    return response