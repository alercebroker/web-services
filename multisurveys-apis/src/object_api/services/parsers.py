from .statements_sql import (
    convert_conesearch_args,
    convert_filters_to_sqlalchemy_statement,
    create_conesearch_statement,
)
from ..models.object import ObjectOutputModels


class ModelParserOutput():

    def __init__(self, survey: str, input_data: dict, probability: bool = False):
        self.survey = survey
        self.input_data = input_data
        self.probability = probability

    def parse_data(self):
        output_model = ObjectOutputModels(self.survey, self.probability).get_model_by_survey()
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
        model_parsed = ModelParserOutput(survey, model_dict).parse_data()
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

        model_output = ModelParserOutput(survey, item_dict, True).parse_data()
        ret.append(model_output)

    return ret