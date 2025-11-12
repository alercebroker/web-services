from db_plugins.db.sql.models import (
    Object,
    ZtfObject,
    LsstDiaObject,
    Probability,
)
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_
from object_api.services.statements_sql import (
    create_order_statement,
    add_limits_statements,
)
from object_api.models.pagination import Pagination


class ObjectsModels:
    def __init__(self, survey):
        self.survey = survey

    def get_model_by_survey(self):
        s = (self.survey or "").lower()
        if s == "ztf":
            return ZtfObject
        if s == "lsst":
            return LsstDiaObject
        # fallback to generic Object so callers don't break for unknown surveys
        return Object


def query_object_by_id(session_ms, oid, survey_id):
    """Query a single object joining the common `Object` table and the survey-specific table.

    Returns the row containing (survey_model, Object) similar to detections' queries.
    """
    with session_ms() as session:
        model = ObjectsModels(survey_id).get_model_by_survey()

        stmt = build_statement_object(model, oid)

        object_row = session.execute(stmt).one()

        return object_row


def build_statement_object(model_id, oid):
    # Select both the survey-specific model and the common Object and join them by oid
    stmt = (
        select(model_id, Object)
        .join(Object, and_(Object.oid == model_id.oid))
        .where(and_(model_id.oid == oid))
        .limit(1)
    )

    return stmt


def query_get_objects(session_ms, search_params, parsed_params):
    filter_args = search_params.filter_args
    filters_statements = parsed_params["filters_sqlalchemy_statement"]
    pagination_args = check_pagination_args(search_params.pagination_args)

    with session_ms() as session:
        object_alias, dinamic_model_alias = build_subquery_object(
            filter_args.survey, filters_statements["objects"], parsed_params
        )

        stmt = (
            select(Probability, object_alias, dinamic_model_alias)
            .join(
                dinamic_model_alias,
                and_(dinamic_model_alias.oid == Probability.oid),
            )
            .where(*filters_statements["probability"])
        )

        order_statement = create_order_statement(stmt, search_params.order_args)

        stmt = stmt.order_by(order_statement)

        stmt = add_limits_statements(stmt, pagination_args)

        items = session.execute(stmt).all()

        return Pagination(pagination_args.page, pagination_args.page_size, items)


def build_subquery_object(survey, filters, parsed_params):
    model_id = ObjectsModels(survey).get_model_by_survey()
    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    stmt = (
        select(Object, model_id)
        .join(model_id, and_(model_id.oid == Object.oid))
        .where(*filters)
        .where(consearch)
        .params(**consearch_args)
        .subquery()
    )

    object_alias = aliased(Object, stmt)
    dinamic_model_alias = aliased(model_id, stmt)

    return object_alias, dinamic_model_alias


def check_pagination_args(pagination_args):
    if pagination_args.page < 1:
        pagination_args.page = 1
    if pagination_args.page_size < 0:
        pagination_args.page_size = 10

    return pagination_args
