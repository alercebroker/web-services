from core.repository.queries.classifiers import get_all_classifiers
from classifier_api.services.classifiers import get_classifiers
from .classifiers_utils import sort_classifiers
from core.repository.queries.objects import query_get_objects, query_object_by_id
from ..services.parsers import parse_to_json_classifiers
from .classifier_data_matcher import update_filters
from .parsers import (
    parse_params,
    parse_objects_list_output,
    parse_unique_object_query,
    parse_classifiers
)


def get_object_by_id(session_ms, oid, survey_id):

    object_model = query_object_by_id(session_ms, oid, survey_id)
    response = parse_unique_object_query(object_model, survey_id)

    return response


def get_objects_list(session_ms, search_params):

    classes_list = get_classes_list(session_ms)
    search_params = update_filters(search_params, classes_list)
    parsed_params = parse_params(search_params)

    result = query_get_objects(session_ms, search_params, parsed_params)
    result = parse_objects_list_output(result, search_params.filter_args.survey, classes_list)

    return result


def get_classes_list(session_ms):
    classes_list = get_all_classifiers(session_ms)
    classes_list_parsed = parse_classifiers(classes_list)

    return classes_list_parsed


def get_tidy_classifiers(session_ms):
    classifiers = get_classifiers(session_ms)
    classifiers = parse_to_json_classifiers(classifiers)
    classifiers = sort_classifiers(classifiers)

    return classifiers