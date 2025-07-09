from .statements_sql import (
    convert_conesearch_args,
    convert_filters_to_sqlalchemy_statement,
    create_conesearch_statement,
)
from ..models.object import ExportModel


class ModelDataParser():

    def __init__(self, survey: str, input_data: dict, model_variant: str = "basic"):
        self.survey = survey
        self.input_data = input_data
        self.model_variant = model_variant

    def parse_data(self):
        output_model = ExportModel(self.survey, self.model_variant).get_model()
        model_parsed = output_model(**self.input_data)

        return model_parsed


def parse_params(search_params):
    consearch_parse = convert_conesearch_args(
        search_params.conesearch_args.__dict__
    )
    consearch_statement = create_conesearch_statement(consearch_parse)
    filters_sqlalchemy_statement = convert_filters_to_sqlalchemy_statement(
        search_params.filter_args.__dict__
    )

    response = {
        "consearch_args": consearch_parse,
        "consearch_statement": consearch_statement,
        "filters_sqlalchemy_statement": filters_sqlalchemy_statement,
    }

    return response


def parse_unique_object_query(sql_response, survey):
    parsed_dict = {}
    for model in sql_response:
        model_dict = model.__dict__.copy()
        model_parsed = ModelDataParser(survey, model_dict).parse_data()
        parsed_dict.update(model_parsed)

    return parsed_dict



def parse_objects_list_output(result, survey):

    return {
        "total": result.total,
        "next": result.next_num,
        "has_next": result.has_next,
        "prev": result.prev_num,
        "has_prev": result.has_prev,
        "items": serialize_items(result.items, survey),
    }


def serialize_items(data, survey):
    ret = []
    for sql_row in data:
        item_dict = {}
        for sql_model in sql_row:
            model_data = sql_model.__dict__.copy()
            item_dict.update(model_data)

        model_output = ModelDataParser(survey, item_dict, "probability").parse_data()
        ret.append(model_output)

    return ret