"""P2-2: a list with no order column (order_by=oid_list, or none) still respects page_size."""

from contextlib import contextmanager

import pytest
from sqlalchemy.dialects import postgresql

from core.repository.queries.objects import query_get_objects
from object_api.models.filters import Consearch, Filters, SearchParams
from object_api.models.pagination import Order, PaginationArgs
from object_api.services.parsers import parse_params


class Captured(Exception):
    pass


@contextmanager
def capturing_session():
    class Session:
        def execute(self, stmt):
            raise Captured(stmt)

    yield Session()


def list_sql(order_by, oids=None, page=1):
    search_params = SearchParams(
        filter_args=Filters(survey="ztf", oids=oids, ranking=1),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=page, page_size=20, count=False),
        order_args=Order(order_by=order_by, order_mode="DESC"),
    )

    with pytest.raises(Captured) as captured:
        query_get_objects(capturing_session, search_params, parse_params(search_params))

    stmt = captured.value.args[0]
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


@pytest.mark.parametrize("order_by", ["oid_list", None])
def test_list_without_order_is_paged(order_by):
    assert "LIMIT 21 OFFSET 40" in list_sql(order_by, page=3)


@pytest.mark.parametrize("order_by", ["oid_list", None])
def test_list_without_order_has_a_stable_order(order_by):
    sql = list_sql(order_by, page=3)

    assert "ORDER BY tprobability.oid" in sql
    assert sql.index("ORDER BY") < sql.index("LIMIT")


def test_oid_list_is_bounded_by_the_oids_asked_for():
    sql = list_sql("oid_list", oids=[36028797018963968, 36028797018963969])

    assert "36028797018963968" in sql and "36028797018963969" in sql
    assert "LIMIT" not in sql  # the page is cut in Python, in the order of the list
