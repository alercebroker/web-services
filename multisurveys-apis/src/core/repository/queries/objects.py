from typing import Callable
from db_plugins.db.sql.models import Object, ZtfObject
from sqlalchemy.orm import aliased, Session

def query_get_objects(
        session_factory, 
        search_params, 
        parsed_params
    ):
    print(session_factory)

    classifer_name = search_params.filter_args.classifier
    classifier_version = search_params.filter_args.classifier_version
    ranking = search_params.filter_args.ranking
    oids = search_params.filter_args.oids

    order_by = search_params.order_args.order_by
    order_mode = search_params.order_args.order_mode

    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    filters = parsed_params["filters_sqlalchemy_statement"]
    
    with session_factory as session:

        all_objects = (
            session.query(Object)
            .join(ZtfObject, Object.oid==ZtfObject.oid).all()
        )

        # join_table = (
        #     session.query(models.Probability)
        #     .filter(models.Probability.classifier_name == classifer_name)
        #     .filter(models.Probability.classifier_version == classifier_version)
        #     .filter(models.Probability.ranking == ranking)
        #     .subquery("probability")
        # )

        # join_table = aliased(models.Probability, join_table)

        # query = (
        #     session.query(models.Object, join_table)
        #     .outerjoin(join_table)
        #     .filter(consearch)
        #     .filter(*filters)
        #     .params(**consearch_args)
        # )

        order_statement = create_order_statement(all_objects, oids, order_by, order_mode)

    pass


def create_order_statement(query, oids, order_by, order_mode):
    statement = None
    cols = query.column_descriptions
    print(order_by, order_mode, oids)

    return statement