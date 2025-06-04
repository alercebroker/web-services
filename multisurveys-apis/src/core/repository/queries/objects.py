from typing import Callable
from db_plugins.db.sql.models import Object, ZtfObject
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from object_api.services.statements_sql import create_order_statement
from object_api.models.pagination import Pagination


def query_object_by_id(session_ms, id):
    
    with session_ms() as session:
        object, ztf_object = (
            session
            .query(Object)
            .join(ZtfObject, Object.oid==ZtfObject.oid)
            .add_entity(ZtfObject)
            .filter(Object.oid == id)
            .one()
        )

        return object, ztf_object



def query_get_objects(session_ms, search_params, parsed_params):

    filter_args = search_params.filter_args
    order_args = search_params.order_args
    pagination_args = search_params.pagination_args

    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    filters_statements = parsed_params["filters_sqlalchemy_statement"]

    with session_ms() as session:
        all_objects = (
            session.query(Object)
            .join(ZtfObject, Object.oid == ZtfObject.oid)
        )

        # join_table = (
        #     session.query(models.Probability)
        #     .filter(models.Probability.classifier_name == filter_args.classifer_name)
        #     .filter(models.Probability.classifier_version == filter_args.classifier_version)
        #     .filter(models.Probability.ranking == filter_args.ranking)
        #     .subquery("probability")
        # )

        # join_table = aliased(models.Probability, join_table)

        # query = (
        #     session.query(all_objects, join_table)
        #     .outerjoin(join_table)
        #     .filter(consearch)
        #     .filter(*filters_statements)
        #     .params(**consearch_args)
        # )

        order_statement = create_order_statement(
            all_objects, filter_args.oids, order_args
        )

        q = all_objects.order_by(order_statement)

        pagination = paginate(q, pagination_args)

        return pagination


def paginate(
        query, 
        pagination_args,
        max_results=50000
    ):

    if pagination_args.page < 1:
        pagination_args.page = 1
    if pagination_args.page_size < 0:
        pagination_args.page_size = 10
    
    items = query.limit(pagination_args.page_size).offset((pagination_args.page-1) * pagination_args.page_size).all()

    if not pagination_args.count:
        total = None
    else:
        total = query.order_by(None).limit(max_results + 1).count()

    return Pagination(query, pagination_args.page, pagination_args.page_size, total, items)