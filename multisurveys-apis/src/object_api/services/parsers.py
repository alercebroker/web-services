from fastapi.encoders import jsonable_encoder
from .statements_sql import (
    convert_conesearch_args,
    convert_filters_to_sqlalchemy_statement,
    create_conesearch_statement,
)
from .classifier_data_matcher import match_and_update_item_class
from .classifiers_utils import format_classifier_name
from ..models.object import ExportModel
from .information_messages import get_info_message
from .idmapper.idmapper import decode_ids


class ModelDataParser:
    def __init__(self, survey: str, input_data: dict, model_variant: str = "basic"):
        self.survey = survey
        self.input_data = input_data
        self.model_variant = model_variant

    def parse_data(self):
        output_model = ExportModel(self.survey, self.model_variant).get_model()
        model_parsed = output_model(**self.input_data)
        json_model = jsonable_encoder(model_parsed)

        return json_model


def parse_params(search_params):
    consearch_parse = convert_conesearch_args(search_params.conesearch_args.__dict__)
    consearch_statement = create_conesearch_statement(consearch_parse)
    filters_sqlalchemy_statement = convert_filters_to_sqlalchemy_statement(search_params.filter_args.__dict__)

    response = {
        "consearch_args": consearch_parse,
        "consearch_statement": consearch_statement,
        "filters_sqlalchemy_statement": filters_sqlalchemy_statement,
    }

    return response

import pprint
def parse_unique_object_query(sql_response, survey, return_survey_extra=False):
    # Merge the dicts from the joined SQLAlchemy models (common Object + survey-specific)
    merged_dict = {}

    for model in sql_response:
        # model is typically a SQLAlchemy mapped object; copy its __dict__ and drop SA internals
        if hasattr(model, "__dict__"):
            model_data = model.__dict__.copy()
            model_data.pop("_sa_instance_state", None)
            merged_dict.update(model_data)
        else:
            # If model is already a dict-like mapping, merge directly
            try:
                merged_dict.update(dict(model))
            except Exception:
                # fallback: skip unsupported entries
                continue

    if return_survey_extra:
        model_variant = "with_extra"
    else:
        model_variant = "basic"

    # Parse the merged dict once with the appropriate ExportModel for the survey
    model_parsed = ModelDataParser(survey, merged_dict, model_variant).parse_data()

    return model_parsed


def parse_objects_list_output(result, survey, classes_list):
    items = serialize_items(result.items_page)
    items_updated = match_and_update_item_class(items, classes_list)
    items_output = parse_items_probabilities(items_updated, survey)
    if survey == "ztf":
        items_output = decode_ids(items_output)
    info_message = get_info_message(items_output)

    return {
        "total": result.total_items,
        "next": result.next_num,
        "has_next": result.has_next,
        "prev": result.prev_num,
        "has_prev": result.has_prev,
        "current_page": result.page,
        "items": items_output,
        "info_message": info_message,
    }


def serialize_items(data):
    ret = []
    for sql_row in data:
        item_dict = {}
        for sql_model in sql_row:
            model_data = sql_model.__dict__.copy()
            item_dict.update(model_data)

        ret.append(item_dict)

    return ret


def parse_items_probabilities(items, survey):
    ret = []
    for item in items:
        model_output = ModelDataParser(survey, item, "probability").parse_data()
        ret.append(model_output)

    return ret


def parse_classifiers(classes_list):
    res = []
    for class_name in classes_list:
        classifier_ms = jsonable_encoder(class_name[0], exclude={"_sa_instance_state"})
        taxonomy_ms = jsonable_encoder(class_name[1], exclude={"_sa_instance_state"})
        merged_dict = {**classifier_ms, **taxonomy_ms}

        res.append(merged_dict)

    return res


def parse_to_json_classifiers(classifiers):
    res = []
    for classifier in classifiers:
        item = jsonable_encoder(classifier)
        item["formated_name"] = format_classifier_name(item["classifier_name"])
        res.append(item)

    return res
