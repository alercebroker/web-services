from itertools import groupby

import pandas as pd
from db_plugins.db.sql.models_pipeline import (
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
from core.exceptions import ObjectNotFound


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

        object_row = session.execute(stmt).one_or_none()

    # Raised after the session closes: db-plugins' session() re-raises anything raised inside it as a bare
    # Exception, which would turn this 404 into a 500
    if object_row is None:
        raise ObjectNotFound(oid)
    return object_row


def query_object_by_id(session_ms, oid, survey_id):
    """Query a single object joining the common `Object` table and the survey-specific table.

    Returns the row containing (survey_model, Object) similar to detections' queries.
    """
    with session_ms() as session:
        model = ObjectsModels(survey_id).get_model_by_survey()

        stmt = build_statement_object(model, oid)

        object_row = session.execute(stmt).one_or_none()

    # Raised after the session closes: db-plugins' session() re-raises anything raised inside it as a bare
    # Exception, which would turn this 404 into a 500
    if object_row is None:
        raise ObjectNotFound(oid)
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

    page = select(probability_alias, object_alias).join(
        object_alias,
        and_(object_alias.oid == probability_alias.oid),
    )
    page_order = create_order_statement(page, search_params.order_args)

    with session_ms() as session:
        if len(page_order) > 0:
            stmt = page_then_survey_statement(
                page, page_order, dynamic_object_alias, search_params.order_args, pagination_args
            )
        else:
            stmt = (
                select(probability_alias, object_alias, dynamic_object_alias)
                .join(
                    object_alias,
                    and_(object_alias.oid == probability_alias.oid),
                )
                .join(
                    dynamic_object_alias,
                    and_(dynamic_object_alias.oid == probability_alias.oid),
                )
            )

            # No order column (none, or "oid_list"). With an oid list the rows are bounded by
            # that list and paged in sort_by_oid_list_and_select_page; without one, page here.
            if search_params.filter_args.oids is None:
                stmt = add_limits_statements(stmt, pagination_args)

        items = session.execute(stmt).all()

        items = order_by_oid(items, search_params.order_args)

        if (
            search_params.filter_args.oids is not None
            and search_params.order_args.order_by in (None, "oid_list")
            and len(items) > 0
        ):
            items = sort_by_oid_list_and_select_page(search_params, items)

        return Pagination(pagination_args.page, pagination_args.page_size, items)


def page_then_survey_statement(page, page_order, survey_model, order_args, pagination_args):
    """Pick the page's rows from probability and object, then join the survey table to those rows only.

    In one flat query Postgres joins the survey table before ORDER BY ... LIMIT, so while it walks objects
    in sort order looking for matches it may look up the survey row of every object it passes, not just of
    the page's (25,026 lsst_dia_object lookups for a 51-row LSST page at offset 50,000). It can't defer the
    join itself: without foreign keys it can't know the inner join drops no rows. The pipeline keeps every
    object with exactly one survey row, so joining after the LIMIT returns the same rows.

    The outer ORDER BY only re-sorts the page's rows; the LIMIT and OFFSET stay inside.
    """
    page = add_limits_statements(page.order_by(*page_order), pagination_args).subquery("tpage")
    probability_page = aliased(Probability, page)
    object_page = aliased(Object, page)

    stmt = select(probability_page, object_page, survey_model).join(
        survey_model,
        and_(survey_model.oid == probability_page.oid),
    )

    return stmt.order_by(*create_order_statement(stmt, order_args))


def order_by_oid(items, order_args):
    """Complementary oid desc order applied to the rows already fetched.

    The main order is preserved: only consecutive rows with the same value in the
    order column are reordered among themselves. Does nothing when there is no
    main order or it is "oid_list" (defined by the user-supplied oid list).
    """
    order_by = order_args.order_by
    if order_by is None or order_by == "oid_list":
        return items

    ordered = []
    for _, group in groupby(items, key=lambda row: order_value(row, order_by)):
        ordered.extend(sorted(group, key=lambda row: row[0].oid, reverse=True))

    return ordered


def order_value(row, order_by):
    """Value of the order column in a row of models (probability, object, survey object)."""
    models = [row[1]] if order_by == "lastmjd" else row
    for model in models:
        if hasattr(model, order_by):
            return getattr(model, order_by)

    return None


def subquery_probability(filters):
    stmt = select(Probability).where(*filters).cte("tprobability")

    probability_alias = aliased(Probability, stmt)

    return probability_alias


def subquery_object(filters, parsed_params):
    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]

    stmt = select(Object).where(*filters).where(consearch).params(**consearch_args).cte("tobject")

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
