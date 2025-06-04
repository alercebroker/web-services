from .statements_sql import (
    convert_conesearch_args,
    convert_filters_to_sqlalchemy_statement,
    create_conesearch_statement,
)


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
    for obj in data:
        obj = {**obj.__dict__}
        ret.append({**obj})
    return ret