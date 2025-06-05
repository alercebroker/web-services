import pprint
from .statements_sql import (
    convert_conesearch_args,
    convert_filters_to_sqlalchemy_statement,
    create_conesearch_statement,
)
from fastapi.encoders import jsonable_encoder

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


def parse_result_query(sql_response):
    parsed_dict = {}
    for row in sql_response:
        row_parsed = jsonable_encoder(row, sqlalchemy_safe=True)
        parsed_dict.update(row_parsed)

    return parsed_dict


def parse_objects_list_output(result):

    return {
        "total": result.total,
        "next": result.next_num,
        "has_next": result.has_next,
        "prev": result.prev_num,
        "has_prev": result.has_prev,
        "items": serialize_items(result.items),
    }


def serialize_items(data):
    ret = []
    for sql_row in data:
        item_dict = {}
        for sql_model in sql_row:
            model_dict = jsonable_encoder(sql_model, sqlalchemy_safe=True)
            item_dict.update(model_dict)

        ret.append(item_dict)

    return ret