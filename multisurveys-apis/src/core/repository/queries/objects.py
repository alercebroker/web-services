import pandas as pd
from db_plugins.db.sql.models import (
    Object,
    ZtfObject,
    LsstDiaObject,
    Probability,
)
from sqlalchemy.orm import aliased
from sqlalchemy import select, and_
from object_api.services.parsers import serialize_items
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


def query_common_object(session_ms, oid, survey_id):
    with session_ms() as session:
        model = ObjectsModels(survey_id).get_model_by_survey()

        stmt = select(model).where(and_(model.oid == oid)).limit(1)

        object_row = session.execute(stmt).one()

        return object_row


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
    filters_objects = parsed_params["filters_sqlalchemy_statement"]["objects"]
    filters_probability = parsed_params["filters_sqlalchemy_statement"]["probability"]
    pagination_args = check_pagination_args(search_params.pagination_args)

    probability_alias = subquery_probability(filters_probability)
    object_alias = subquery_object(filters_objects, parsed_params)
    dynamic_object_alias = dinamic_object_model(search_params.filter_args.survey)

    with session_ms() as session:
        stmt = (
            select(probability_alias, object_alias)
            .join(
                object_alias,
                and_(object_alias.oid == probability_alias.oid),
            ).join(
                dynamic_object_alias,
                and_(dynamic_object_alias.oid == probability_alias.oid),
            )
        )

        order_statement = create_order_statement(stmt, search_params.order_args)

        stmt = stmt.order_by(*order_statement)

        if len(order_statement) > 0:
            stmt = add_limits_statements(stmt, pagination_args)

        items = session.execute(stmt).all()

        if search_params.filter_args.oids is not None and search_params.order_args.order_by is None and len(items) > 0:
            items = sort_by_oid_list_and_select_page(search_params, items)

        return Pagination(pagination_args.page, pagination_args.page_size, items)
    

def subquery_probability(filters):

    stmt = (
        select(Probability)
        .where(*filters)
        .subquery()
    )

    probability_alias = aliased(Probability, stmt)

    return probability_alias

def subquery_object(filters, parsed_params):
    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    stmt = (
        select(Object)
        .where(*filters)
        .where(consearch)
        .params(**consearch_args)
        .subquery()
    )

    object_alias = aliased(Object, stmt)

    return object_alias

def dinamic_object_model(survey):
    model_id = ObjectsModels(survey).get_model_by_survey()
    return model_id


def sort_by_oid_list_and_select_page(search_params, items):
    df_items = pd.DataFrame.from_records(items)
    df_items["oid"] = [item["oid"] for item in serialize_items(items)]
    df_items.set_index("oid", inplace=True)
    oid_valid = [x for x in search_params.filter_args.oids if x in df_items.index]
    df_items = df_items.loc[oid_valid].copy()

    page = search_params.pagination_args.page
    page_size = search_params.pagination_args.page_size
    idx_start = (page - 1) * page_size
    idx_end = idx_start + page_size + 1
    df_items = df_items.iloc[idx_start:idx_end].copy()
    df_items = list(df_items.itertuples(index=False, name=None))

    return df_items


def check_pagination_args(pagination_args):
    if pagination_args.page < 1:
        pagination_args.page = 1
    if pagination_args.page_size < 0:
        pagination_args.page_size = 10

    return pagination_args
