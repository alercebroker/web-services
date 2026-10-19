from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from core.repository.queries.objects import query_get_objects
from object_api.routes import htmx, rest
from object_api.models.filters import Consearch, Filters, SearchParams
from object_api.models.pagination import Order, PaginationArgs
from object_api.services.classifier_data_matcher import update_filters
from object_api.services.parsers import parse_params

CLASSES_LIST = [
    {"classifier_id": 5, "classifier_name": "lc_classifier_BHRF_forced_phot", "class_id": 19, "class_name": "TDE"},
]


class Captured(Exception):
    pass


@contextmanager
def capturing_session():
    class Session:
        def execute(self, stmt):
            raise Captured(stmt)

    yield Session()


def list_sql(order_by, page=1):
    search_params = SearchParams(
        filter_args=Filters(survey="ztf", classifier="lc_classifier_BHRF_forced_phot", class_name="TDE", ranking=1),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=page, page_size=20, count=False),
        order_args=Order(order_by=order_by, order_mode="DESC"),
    )
    search_params = update_filters(search_params, CLASSES_LIST)

    with pytest.raises(Captured) as captured:
        query_get_objects(capturing_session, search_params, parse_params(search_params))

    stmt = captured.value.args[0]
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def page_and_after(sql):
    """The page subquery, and what the outer query does after it."""
    before, after = sql.split(") AS tpage", 1)
    return before.split("FROM (", 1)[1], after


@pytest.mark.parametrize("order_by", ["lastmjd", "firstmjd", "n_det", "probability"])
def test_survey_table_is_joined_after_the_page_is_chosen(order_by):
    page, outer = page_and_after(list_sql(order_by, page=3))

    assert "LIMIT 21 OFFSET 40" in page
    assert "ztf_object" not in page
    assert "JOIN ztf_object ON ztf_object.oid = tpage.oid" in outer
    assert "LIMIT" not in outer


def test_lastmjd_sorts_by_the_object_column_inside_and_outside():
    page, outer = page_and_after(list_sql("lastmjd"))

    assert "ORDER BY tobject.lastmjd DESC" in page
    # probability also has a lastmjd column; the page's object one is labelled lastmjd_1.
    assert "ORDER BY tpage.lastmjd_1 DESC" in outer


@pytest.mark.parametrize("order_by", ["ndethist", None])
def test_sort_on_a_survey_column_or_no_sort_keeps_the_single_query(order_by):
    sql = list_sql(order_by)

    assert "tpage" not in sql
    assert "JOIN ztf_object ON ztf_object.oid = tprobability.oid" in sql


def compiled_sql(search_params):
    search_params = update_filters(search_params, CLASSES_LIST)

    with pytest.raises(Captured) as captured:
        query_get_objects(capturing_session, search_params, parse_params(search_params))

    stmt = captured.value.args[0]
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def object_api_client():
    app = FastAPI()
    app.include_router(htmx.router)
    app.include_router(rest.router)
    app.state.psql_session = None
    return TestClient(app)


@pytest.fixture
def route_sql(monkeypatch):
    """GET a route of the object API and return the SQL it would run."""
    sqls = []

    def fake_get_objects_list(session_ms, search_params):
        sqls.append(compiled_sql(search_params))
        return {"next": False, "has_next": False, "prev": False, "has_prev": False, "items": []}

    monkeypatch.setattr(htmx, "get_objects_list", fake_get_objects_list)
    monkeypatch.setattr(rest, "get_objects_list", fake_get_objects_list)
    client = object_api_client()

    def get(path, **params):
        response = client.get(
            path,
            params={"survey": "ztf", "classifier": CLASSES_LIST[0]["classifier_name"], "class_name": "TDE", **params},
        )
        assert response.status_code == 200, response.text
        return sqls[-1]

    return get


@pytest.mark.parametrize("path", ["/htmx/list_objects", "/htmx/side_objects"])
@pytest.mark.parametrize(
    "params, expected",
    [
        ({"firstmjd_min": 60000}, "object.firstmjd >= 60000.0 AND object.sid"),
        ({"firstmjd_max": 60100}, "object.firstmjd >= 0.0 AND object.firstmjd <= 60100.0"),
        ({"firstmjd_min": 60000, "firstmjd_max": 60100}, "object.firstmjd >= 60000.0 AND object.firstmjd <= 60100.0"),
    ],
    ids=["min_only", "max_only", "both"],
)
def test_website_discovery_date_bounds_firstmjd(route_sql, path, params, expected):
    sql = route_sql(path, **params)

    assert expected in sql
    assert "object.lastmjd >=" not in sql


def test_website_ignores_the_old_lastmjd_parameter(route_sql):
    sql = route_sql("/htmx/list_objects", lastmjd=60100)

    assert "WHERE object.sid = 0)" in sql


def test_website_rejects_min_after_max():
    response = object_api_client().get(
        "/htmx/list_objects", params={"survey": "ztf", "firstmjd_min": 60100, "firstmjd_max": 60000}
    )

    assert response.status_code == 422
    assert "discovery_date_filters_container" in response.json()["detail"]


def test_rest_keeps_firstmjd_and_lastmjd_lists(route_sql):
    sql = route_sql("/list_objects", firstmjd=[60000, 60100], lastmjd=[60200])

    assert "object.firstmjd >= 60000.0 AND object.firstmjd <= 60100.0" in sql
    assert "object.lastmjd >= 60200.0" in sql


def probability_where(**filter_args):
    """The WHERE clause of the probability CTE, for a TDE list with these extra filters."""
    filter_args = {"survey": "ztf", "classifier": "lc_classifier_BHRF_forced_phot", "class_name": "TDE", **filter_args}
    search_params = SearchParams(
        filter_args=Filters(ranking=1, **filter_args),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=1, page_size=20, count=False),
        order_args=Order(order_by="probability", order_mode="DESC"),
    )
    sql = compiled_sql(search_params)
    cte = sql.split("WITH tprobability AS", 1)[1].split("tobject AS", 1)[0]
    return cte.split("WHERE", 1)[1]


def test_prob_lastmjd_range_filters_probability():
    where = probability_where(prob_lastmjd_min=61300.0, prob_lastmjd_max=61330.0)

    assert "probability.lastmjd >= 61300.0" in where
    assert "probability.lastmjd <= 61330.0" in where


def test_object_dates_imply_bounds_on_prob_lastmjd():
    where = probability_where(firstmjd=[61328.0], lastmjd=[61000.0, 61340.0])

    assert "probability.lastmjd >= 61328.0" in where
    assert "probability.lastmjd <= 61340.0" in where


def test_bounds_that_imply_nothing_add_no_prob_lastmjd_filter():
    # lastmjd with one value is a lower bound on the last detection, which says nothing about probability.lastmjd.
    assert "probability.lastmjd" not in probability_where(lastmjd=[61000.0])
    assert "probability.lastmjd" not in probability_where(classifier=None, class_name=None, firstmjd=[61328.0])


def test_prob_lastmjd_needs_a_classifier_and_an_ordered_range():
    from fastapi import HTTPException

    from object_api.services.validations import prob_lastmjd_validation

    prob_lastmjd_validation(None, None, None)
    prob_lastmjd_validation(61300.0, None, "lc_classifier_BHRF_forced_phot")
    for args in [(61300.0, None, None), (61330.0, 61300.0, "lc_classifier_BHRF_forced_phot")]:
        with pytest.raises(HTTPException) as error:
            prob_lastmjd_validation(*args)
        assert error.value.status_code == 422
        assert "classifier_date_filters_container" in error.value.detail
