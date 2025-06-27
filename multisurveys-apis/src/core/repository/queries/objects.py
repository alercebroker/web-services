from db_plugins.db.sql.models import Object, ZtfObject, LsstSsObject
from sqlalchemy.orm import aliased
from sqlalchemy import select, text
from object_api.services.statements_sql import create_order_statement, add_limits_statements
from object_api.models.pagination import Pagination
from core.repository.models.probability import Probability


class subquery_objects():

    def __init__(self, survey, filters, parsed_params):
        self.survey = survey
        self.filters = filters
        self.consearch = parsed_params["consearch_statement"]
        self.consearch_args = parsed_params["consearch_args"]
        
    def build_subquery_object(self):
        model_id = objects_models(self.survey).get_model_id()

        print(self.consearch, self.consearch_args)

        stmt = (
            select(Object, model_id)
            .join(model_id, model_id.oid == Object.oid)
            .where(*self.filters)
            .where(self.consearch)
            .params(**self.consearch_args)
            .subquery()
        )
        
        object_alias = aliased(Object, stmt)
        dinamic_model_alias = aliased(model_id, stmt)

        return object_alias, dinamic_model_alias


class objects_models():
    def __init__(self, survey):
        self.survey = survey

    def get_model_id(self):
        if self.survey == "ztf":
            return ZtfObject
        if self.survey == "lsst":
            return LsstSsObject 
        

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
    pagination_args = check_pagination_args(search_params.pagination_args)

    filters_statements = parsed_params["filters_sqlalchemy_statement"]

    with session_ms() as session:

        object_alias, dinamic_model_alias = subquery_objects(filter_args.survey, filters_statements["objects"], parsed_params).build_subquery_object()

        stmt = select(Probability, object_alias, dinamic_model_alias).join(dinamic_model_alias, dinamic_model_alias.oid == Probability.oid).where(*filters_statements["probability"])

        order_statement = create_order_statement(stmt, order_args)

        stmt = stmt.order_by(order_statement)

        total = calculate_total_items(stmt, pagination_args)

        stmt = add_limits_statements(stmt, pagination_args)

        items = session.execute(stmt).all()


        print(items)
        return Pagination(pagination_args.page, pagination_args.page_size, total, items)


# def build_subquery_object(model_id, filters):

#     stmt = (
#         select(Object, model_id)
#         .join(model_id, model_id.oid == Object.oid)
#         .where(*filters)
#         .subquery()
#     )
    
#     return stmt


def check_pagination_args(pagination_args):
    if pagination_args.page < 1:
        pagination_args.page = 1
    if pagination_args.page_size < 0:
        pagination_args.page_size = 10
    
    return pagination_args


def calculate_total_items(stmt, pagination_args, max_results=50000):
    if not pagination_args.count:
        total = None
    else:
        total = stmt.order_by(None).limit(max_results + 1).count()

    return total
