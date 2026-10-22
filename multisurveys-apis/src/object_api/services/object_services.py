from core.repository.queries.classifiers import get_all_classifiers
from classifier_api.services.classifiers import get_classifiers
from core.idmapper.survey_mapper import get_survey_id
from core.repository.queries.objects import (
    query_get_objects,
    query_object_by_id,
    query_objects_with_prediction,
)
from core.idmapper.idmapper import encode_ids
from ..services.parsers import parse_to_json_classifiers
from .classifier_data_matcher import update_filters
from .parsers import (
    parse_params,
    parse_objects_list_output,
    parse_unique_object_query,
    parse_classifiers,
)


def get_object_by_id(oid, survey_id: str, session_ms, return_survey_extra: bool = False):
    oid_encode = encode_ids(survey_id, [oid])
    object_model = query_object_by_id(session_ms, int(oid_encode[0]), survey_id)

    response = parse_unique_object_query(object_model, survey_id, return_survey_extra)
    return response


# The classifier whose predictions the website shows when no classifier filter is set. Stamp classifiers
# predict every object; the light curve ones only objects with enough detections.
DEFAULT_SHOWN_CLASSIFIER = {
    "ztf": "stamp_classifier",
    "lsst": "stamp_classifier_rubin_beta_20260421",
}


def get_objects_list(session_ms, search_params, shown_classifier: str | None = None):
    """The page of objects, from the probability table (one row per prediction that passes the filters).

    With a shown_classifier and no classifier filter, the page comes from the object table instead: one row per
    object, with that classifier's top class, or none if the classifier has no prediction for it.
    """
    classes_list = get_classes_list(session_ms)
    search_params = update_filters(search_params, classes_list)
    parsed_params = parse_params(search_params)

    if shown_classifier is not None and search_params.filter_args.classifier is None:
        classifier_id = next(c["classifier_id"] for c in classes_list if c["classifier_name"] == shown_classifier)
        result = query_objects_with_prediction(session_ms, search_params, parsed_params, classifier_id)
    else:
        result = query_get_objects(session_ms, search_params, parsed_params)

    result = parse_objects_list_output(result, search_params, classes_list)

    return result


def choose_shown_classifier(survey_classifiers: list, classifier: str | None, shown_classifier: str | None) -> str:
    """The classifier filter if there is one, else the requested one if the survey has it, else the default."""
    names = [c["classifier_name"] for c in survey_classifiers]
    survey = survey_classifiers[0]["survey_id"] if survey_classifiers else None

    for name in [classifier, shown_classifier, DEFAULT_SHOWN_CLASSIFIER.get(survey)]:
        if name in names:
            return name

    return names[0] if names else None


def get_survey_classifiers(session_ms, survey: str) -> list:
    return [c for c in get_website_classifiers(session_ms, survey) if c["survey_id"] == survey]


# The classifiers the website offers, by survey, in the order it lists them: the search form's Classifier filter
# and the results' "Predictions from" selector. The database has others, such as the light curve classifier's
# sub-models (periodic, stochastic, transient, top), that the website leaves out.
WEBSITE_CLASSIFIERS = {
    "ztf": ["lc_classifier_BHRF_forced_phot", "stamp_classifier", "stamp_classifier_2025_beta"],
    "lsst": ["stamp_classifier_rubin_beta_20260421", "stamp_classifier_rubin_beta"],
}


def get_website_classifiers(session_ms, survey_id: str) -> list:
    classifiers = {(c["survey_id"], c["classifier_name"]): c for c in get_tidy_classifiers(session_ms, survey_id)}

    return [
        classifiers[(survey, name)]
        for survey, names in WEBSITE_CLASSIFIERS.items()
        for name in names
        if (survey, name) in classifiers
    ]


def get_classes_list(session_ms):
    classes_list = get_all_classifiers(session_ms)
    classes_list_parsed = parse_classifiers(classes_list)

    return classes_list_parsed


def get_tidy_classifiers(session_ms, survey_id: str):
    survey_id_mapped = get_survey_id(survey_id)

    classifiers = get_classifiers(session_ms, survey_id_mapped)
    classifiers = parse_to_json_classifiers(classifiers)

    return classifiers
