from db_plugins.db.sql.models import Object, ZtfObject, LsstSsObject
from sqlalchemy import select
from object_api.services.statements_sql import create_order_statement
from object_api.models.pagination import Pagination
from core.repository.models.probability import Probability


def query_object_by_id(session_ms, oid, survey_id):
    
    with session_ms() as session:

        if survey_id == "ztf":
            stmt = build_statement_object(ZtfObject, oid)
        
        object = session.execute(stmt).one()

        return object


def build_statement_object(model_id, oid):
    stmt = select(model_id).where(model_id.oid==oid)
    
    return stmt


def query_get_objects(session_ms, search_params, parsed_params):

    filter_args = search_params.filter_args
    order_args = search_params.order_args
    print(order_args)
    pagination_args = check_pagination_args(search_params.pagination_args)

    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    filters_statements = parsed_params["filters_sqlalchemy_statement"]

    with session_ms() as session:

        if filter_args.survey == "ztf":
            subquery_stmt = build_subquery_object(ZtfObject, filters_statements["objects"])
        elif filter_args.survey == "lsst":
            subquery_stmt = build_subquery_object(LsstSsObject, filters_statements["objects"])

        
        stmt = select(Probability).join(subquery_stmt, subquery_stmt.c.oid == Probability.oid).where(*filters_statements["probability"]).where(consearch).params(**consearch_args)

        total = calculate_total_items(stmt, pagination_args)

        stmt = add_limits_statements(stmt, pagination_args)

        items = session.execute(stmt).all()

        return Pagination(pagination_args.page, pagination_args.page_size, total, items)

        # all_objects = (
        #     session.query(Object, ZtfObject)
        #     .join(ZtfObject, Object.oid == ZtfObject.oid)
        # )
         
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

        # order_statement = create_order_statement(
        #     all_objects, filter_args.oids, order_args
        # )

        # q = all_objects.order_by(order_statement)

        # pagination = paginate(q, pagination_args)

        # return pagination


def build_subquery_object(model_id, filters):

    stmt = (
        select(Object, model_id)
        .join(model_id, model_id.oid == Object.oid)
        .where(*filters)
        .subquery()
    )
    
    return stmt


def check_pagination_args(pagination_args):
    if pagination_args.page < 1:
        pagination_args.page = 1
    if pagination_args.page_size < 0:
        pagination_args.page_size = 10
    
    return pagination_args


def add_limits_statements(stmt, pagination_args):

    stmt = stmt.limit(pagination_args.page_size).offset((pagination_args.page-1) * pagination_args.page_size)

    return stmt


def calculate_total_items(stmt, pagination_args, max_results=50000):
    if not pagination_args.count:
        total = None
    else:
        total = stmt.order_by(None).limit(max_results + 1).count()

    return total