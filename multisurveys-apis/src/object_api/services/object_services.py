from core.repository.queries.classifiers import get_all_classifiers
from classifier_api.services.classifiers import get_classifiers
from object_api.models.filters import SearchParams
from object_api.models.object import ObjectQueryInformation
from .classifiers_utils import sort_classifiers
from core.repository.queries.objects import (
    query_get_objects,
    query_object_by_id,
)
from ..services.parsers import parse_to_json_classifiers
from .classifier_data_matcher import update_filters
from .parsers import (
    parse_params,
    parse_objects_list_output,
    parse_unique_object_query,
    parse_classifiers,
)


def get_object_by_id(object_filters: ObjectQueryInformation, session_ms, return_survey_extra: bool = False):
    object_model = query_object_by_id(object_filters, session_ms)

    response = parse_unique_object_query(object_model, object_filters.survey_name, return_survey_extra)
    
    return response


def get_objects_list(session_ms, search_params: SearchParams):
    classes_list = get_classes_list(session_ms)
    search_params = update_filters(search_params, classes_list)
    parsed_params = parse_params(search_params)

    result = query_get_objects(session_ms, search_params, parsed_params)
    result = parse_objects_list_output(result, search_params.filter_args.survey, classes_list)

    return result


def get_classes_list(session_ms) -> list:
    classes_list = get_all_classifiers(session_ms)
    classes_list_parsed = parse_classifiers(classes_list)

    return classes_list_parsed


def get_tidy_classifiers(session_ms):
    classifiers = get_classifiers(session_ms)
    classifiers = parse_to_json_classifiers(classifiers)
    classifiers = sort_classifiers(classifiers)

    return classifiers
