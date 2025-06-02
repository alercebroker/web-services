import pprint
from .parsers import convert_conesearch_args, create_conesearch_statement, convert_filters_to_sqlalchemy_statement
from core.repository.queries.objects import query_get_objects

def get_objects_list(session_factory, search_params):

    parsed_params = parse_params(search_params)

    result = query_get_objects(session_factory, search_params, parsed_params)

    pass


def parse_params(search_params):

    consearch_parse = convert_conesearch_args(search_params.conesearch_args.__dict__)
    consearch_statement = create_conesearch_statement(consearch_parse)
    filters_sqlalchemy_statement = convert_filters_to_sqlalchemy_statement(search_params.filter_args.__dict__)

    response = {
        "consearch_args":consearch_parse, 
        "consearch_statement":consearch_statement,
        "filters_sqlalchemy_statement": filters_sqlalchemy_statement
    }

    return response
