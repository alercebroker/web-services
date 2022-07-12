import math
from shared.utils.queries import ObjectQueryFactory

def create_object_args_dict(remove=[]):
    base_args_dict = {
        'oid': ["oid1", "oid2"],
        'firstmjd': 100,
        'lastmjd': 200,
        'ndet': [1, 100],
        'ra': 1,
        'dec': 2,
        'radius': 3600 # revisar si no viene ya en radianes
    }
    for key in remove:
        del base_args_dict[key]
    
    return base_args_dict

def create_object_query_dict(remove=[]):
    base_query_dict = {
        'oid': {'$in': ["oid1", "oid2"]},
        'firstmjd': {'$gte': 100},
        'lastmjd': {'$lte': 200},
        'ndet': {'$gte': 1, '$lte': 100},
        'loc': {'$geoWithin': {'$centerSphere': [[1, 2], math.radians(1)]}}
    }
    for key in remove:
        del base_query_dict[key]
    
    return base_query_dict

def test_object_full_query():
    request_args = create_object_args_dict()
    expected_query = create_object_query_dict()

    result = ObjectQueryFactory(request_args)

    assert result.clean_query == expected_query

def test_object_empty_quert():
    request_args = {}
    expected_query = {}

    result = ObjectQueryFactory(request_args)

    assert result.clean_query == expected_query

def test_object_query_missing_args():
    # no oid
    request_args = create_object_args_dict(remove=['oid'])
    expected_query = create_object_query_dict(remove=['oid'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

    request_args = create_object_args_dict(remove=['firstmjd'])
    expected_query = create_object_query_dict(remove=['firstmjd'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

    request_args = create_object_args_dict(remove=['lastmjd'])
    expected_query = create_object_query_dict(remove=['lastmjd'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

    request_args = create_object_args_dict(remove=['ndet'])
    expected_query = create_object_query_dict(remove=['ndet'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

def test_missing_loc_data():
    request_args = create_object_args_dict(remove=['ra'])
    expected_query = create_object_query_dict(remove=['loc'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

    request_args = create_object_args_dict(remove=['dec'])
    expected_query = create_object_query_dict(remove=['loc'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

    request_args = create_object_args_dict(remove=['radius'])
    expected_query = create_object_query_dict(remove=['loc'])

    result = ObjectQueryFactory(request_args)
    assert result.clean_query == expected_query

def test_object_query_single_oid():
    request_args = create_object_args_dict()
    request_args['oid'] = "oid1"
    expected_query = create_object_query_dict()
    expected_query['oid']['$in'] = ["oid1"]

    result = ObjectQueryFactory(request_args)

    assert result.clean_query == expected_query
