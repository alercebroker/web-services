from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from core.repository.queries.objects import query_get_objects
from object_api.routes import htmx, rest
from object_api.models.filters import Consearch, Filters, SearchParams
from object_api.models.pagination import Order, PaginationArgs
from object_api.services import object_services
from object_api.services.classifier_data_matcher import update_filters
from object_api.services.parsers import parse_params

CLASSES_LIST = [
    {"classifier_id": 5, "classifier_name": "lc_classifier_BHRF_forced_phot", "class_id": 19, "class_name": "TDE"},
    {"classifier_id": 4, "classifier_name": "stamp_classifier", "class_id": 3, "class_name": "SN"},
]

# What the website's classifier selector offers for ZTF.
SURVEY_CLASSIFIERS = [
    {"classifier_name": "lc_classifier_BHRF_forced_phot", "classifier_id": 5, "survey_id": "ztf"},
    {"classifier_name": "stamp_classifier", "classifier_id": 4, "survey_id": "ztf"},
]


@pytest.fixture(autouse=True)
def survey_classifiers(monkeypatch):
    monkeypatch.setattr(htmx, "get_survey_classifiers", lambda session, survey: SURVEY_CLASSIFIERS)
    monkeypatch.setattr(object_services, "get_classes_list", lambda session: CLASSES_LIST)


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

    def fake_get_objects_list(session_ms, search_params, shown_classifier=None):
        with pytest.raises(Captured) as captured:
            object_services.get_objects_list(capturing_session, search_params, shown_classifier)

        stmt = captured.value.args[0]
        sqls.append(str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))
        return {"next": False, "has_next": False, "prev": False, "has_prev": False, "items": []}

    monkeypatch.setattr(htmx, "get_objects_list", fake_get_objects_list)
    monkeypatch.setattr(rest, "get_objects_list", fake_get_objects_list)
    client = object_api_client()

    def get(path, **params):
        # None leaves out a default parameter.
        params = {"survey": "ztf", "classifier": CLASSES_LIST[0]["classifier_name"], "class_name": "TDE", **params}
        response = client.get(path, params={k: v for k, v in params.items() if v is not None})
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


@pytest.mark.parametrize("path", ["/htmx/list_objects", "/htmx/side_objects"])
@pytest.mark.parametrize(
    "params, expected",
    [
        ({"lastmjd_min": 60000}, "object.lastmjd >= 60000.0 AND object.sid"),
        ({"lastmjd_max": 60100}, "object.lastmjd >= 0.0 AND object.lastmjd <= 60100.0"),
        ({"lastmjd_min": 60000, "lastmjd_max": 60100}, "object.lastmjd >= 60000.0 AND object.lastmjd <= 60100.0"),
    ],
    ids=["min_only", "max_only", "both"],
)
def test_website_last_alert_date_bounds_lastmjd(route_sql, path, params, expected):
    sql = route_sql(path, **params)

    assert expected in sql
    assert "object.firstmjd >=" not in sql


def test_website_last_alert_date_max_also_bounds_prob_lastmjd(route_sql):
    sql = route_sql("/htmx/list_objects", lastmjd_max=60100)

    assert "probability.lastmjd <= 60100.0" in sql


def test_website_rejects_last_alert_min_after_max():
    response = object_api_client().get(
        "/htmx/list_objects", params={"survey": "ztf", "lastmjd_min": 60100, "lastmjd_max": 60000}
    )

    assert response.status_code == 422
    assert "last_alert_date_filters_container" in response.json()["detail"]


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


@pytest.mark.parametrize(
    "params, expected",
    [
        ({"n_det_min": 5}, "lastmjd"),
        ({}, "lastmjd"),
        ({"classifier": CLASSES_LIST[0]["classifier_name"]}, "probability"),
        ({"n_det_min": 5, "order_by": "n_det"}, "n_det"),
        ({"n_det_min": 5, "order_by": "probability"}, "lastmjd"),
    ],
    ids=["object_filters", "no_filters", "classifier", "user_choice", "probability_needs_a_classifier"],
)
def test_website_default_order_depends_on_classification_filters(monkeypatch, params, expected):
    orders = []

    def fake_get_objects_list(session_ms, search_params, shown_classifier=None):
        orders.append((search_params.order_args.order_by, search_params.order_args.order_mode))
        return {"next": False, "has_next": False, "prev": False, "has_prev": False, "items": []}

    monkeypatch.setattr(htmx, "get_objects_list", fake_get_objects_list)
    response = object_api_client().get("/htmx/list_objects", params={"survey": "ztf", **params})

    assert response.status_code == 200, response.text
    assert orders == [(expected, "DESC")]


def test_website_without_classifier_filter_lists_objects_with_the_shown_prediction(route_sql):
    sql = route_sql("/htmx/list_objects", classifier=None, class_name=None, n_det_min=5, page=2)
    page, outer = page_and_after(sql)

    assert "tprobability" not in sql
    assert "FROM tobject ORDER BY tobject.lastmjd DESC, tobject.oid DESC" in page and "LIMIT 21 OFFSET 20" in page
    assert "probability" not in page
    # Every object of the page stays, with or without a prediction of the default (stamp) classifier.
    assert (
        "LEFT OUTER JOIN probability ON probability.oid = tpage.oid AND probability.sid = tpage.sid "
        "AND probability.classifier_id = 4 AND probability.ranking = 1"
    ) in outer
    assert "LIMIT" not in outer


@pytest.mark.parametrize(
    "shown, expected_id",
    [("lc_classifier_BHRF_forced_phot", 5), ("not_a_ztf_classifier", 4)],
    ids=["chosen", "unknown"],
)
@pytest.mark.parametrize("path", ["/htmx/list_objects", "/htmx/side_objects"])
def test_website_shows_the_chosen_classifier_or_the_default(route_sql, path, shown, expected_id):
    sql = route_sql(path, classifier=None, class_name=None, shown_classifier=shown)

    assert f"probability.classifier_id = {expected_id} AND probability.ranking = 1" in sql


def test_classifier_filter_wins_over_the_shown_classifier(route_sql):
    sql = route_sql("/htmx/list_objects", shown_classifier="stamp_classifier")

    assert "WITH tprobability AS" in sql
    assert "probability.classifier_id = 5" in sql
    assert "LEFT OUTER JOIN" not in sql


def test_website_offers_its_classifiers_in_its_order(monkeypatch):
    # As the database lists them: alphabetical, with the light curve sub-models and both surveys' classifiers.
    names = {
        "ztf": [
            "lc_classifier_BHRF_forced_phot",
            "lc_classifier_BHRF_forced_phot_periodic",
            "lc_classifier_BHRF_forced_phot_top",
            "stamp_classifier",
            "stamp_classifier_2025_beta",
        ],
        "lsst": ["stamp_classifier_rubin_beta", "stamp_classifier_rubin_beta_20260421"],
    }
    database = [{"classifier_name": n, "survey_id": s} for s, survey_names in names.items() for n in survey_names]
    monkeypatch.setattr(object_services, "get_tidy_classifiers", lambda session, survey_id: database)

    offered = [(c["survey_id"], c["classifier_name"]) for c in object_services.get_website_classifiers(None, "ztf")]

    assert offered == [
        ("ztf", "lc_classifier_BHRF_forced_phot"),
        ("ztf", "stamp_classifier"),
        ("ztf", "stamp_classifier_2025_beta"),
        ("lsst", "stamp_classifier_rubin_beta_20260421"),
        ("lsst", "stamp_classifier_rubin_beta"),
    ]
    assert [c["classifier_name"] for c in object_services.get_survey_classifiers(None, "lsst")] == [
        "stamp_classifier_rubin_beta_20260421",
        "stamp_classifier_rubin_beta",
    ]


def test_rest_still_lists_one_row_per_prediction(route_sql):
    sql = route_sql("/list_objects", classifier=None, class_name=None)

    assert "WITH tprobability AS" in sql
    assert "LEFT OUTER JOIN" not in sql


def test_object_without_prediction_keeps_its_row():
    from types import SimpleNamespace

    from object_api.models.pagination import Pagination
    from object_api.services.parsers import parse_objects_list_output
    from core.repository.queries.objects import order_by_oid

    def lsst_object(oid, lastmjd):
        return SimpleNamespace(
            oid=oid, tid=1, sid=1, meanra=1.0, meandec=2.0, firstmjd=61000.0, lastmjd=lastmjd, deltamjd=1.0,
            n_det=3, n_forced=0, n_non_det=0,
        )  # fmt: skip

    prediction = SimpleNamespace(oid=2, classifier_id=4, class_id=3, probability=0.9, ranking=1, lastmjd=61000.0)
    rows = order_by_oid(
        [(None, lsst_object(1, 61300.0), None), (prediction, lsst_object(2, 61300.0), None)],
        Order(order_by="lastmjd", order_mode="DESC"),
    )
    search_params = SearchParams(
        filter_args=Filters(survey="lsst"),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=1, page_size=20, count=False),
        order_args=Order(order_by="lastmjd", order_mode="DESC"),
    )
    classes = [{**CLASSES_LIST[1], "classifier_version": "1.0.4"}]

    items = parse_objects_list_output(Pagination(1, 20, rows), search_params, classes)["items"]

    assert [(i["oid"], i["class_name"], i["probability"], i["lastmjd"]) for i in items] == [
        (2, "SN", 0.9, 61300.0),
        (1, None, None, 61300.0),
    ]


def test_new_ztf_object_without_stellar_keeps_its_row():
    from object_api.models.object import ZtfObjectProbability

    # The newest objects, listed now even without a prediction, may not have stellar set yet.
    row = ZtfObjectProbability(
        oid=1, tid=0, sid=0, meanra=1.0, meandec=2.0, firstmjd=61000.0, lastmjd=61300.0, deltamjd=300.0, n_det=1,
        n_forced=0, n_non_det=0, corrected=False, stellar=None,
    )  # fmt: skip

    assert row.stellar is None and row.class_name is None


@pytest.mark.parametrize("order_by", ["ndethist", "not_a_column"])
def test_website_page_stays_limited_without_an_object_sort_column(route_sql, order_by):
    sql = route_sql("/htmx/list_objects", classifier=None, class_name=None, order_by=order_by)

    assert "LIMIT 21 OFFSET 0) AS tpage" in sql


def test_website_oid_list_without_sort_comes_whole(route_sql):
    sql = route_sql("/htmx/list_objects", classifier=None, class_name=None, oid="ZTF26accgtkq,ZTF26accgtnp")

    assert "LIMIT" not in sql
    assert "object.oid IN" in sql
