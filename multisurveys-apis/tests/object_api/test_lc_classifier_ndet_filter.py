import pytest
from sqlalchemy import and_
from sqlalchemy.dialects import postgresql

from object_api.models.filters import Consearch, Filters, SearchParams
from object_api.models.pagination import Order, PaginationArgs
from object_api.services.classifier_data_matcher import update_filters
from object_api.services.parsers import parse_params
from object_api.services.statements_sql import LC_CLASSIFIER_IDS

# Same ids as the production classifier table (checked 14/10/2026).
CLASSES_LIST = [
    {"classifier_id": 2, "classifier_name": "stamp_classifier_2025_beta", "class_id": 1, "class_name": "SN"},
    {"classifier_id": 5, "classifier_name": "lc_classifier_BHRF_forced_phot", "class_id": 18, "class_name": "SNIa"},
    {
        "classifier_id": 6,
        "classifier_name": "lc_classifier_BHRF_forced_phot_top",
        "class_id": 1,
        "class_name": "Transient",
    },
    {
        "classifier_id": 9,
        "classifier_name": "lc_classifier_BHRF_forced_phot_periodic",
        "class_id": 3,
        "class_name": "LPV",
    },
]


def object_filters_sql(classifier, class_name, n_det=None):
    search_params = SearchParams(
        filter_args=Filters(survey="ztf", classifier=classifier, class_name=class_name, ranking=1, n_det=n_det),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=1, page_size=20, count=False),
        order_args=Order(order_by="firstmjd", order_mode="DESC"),
    )
    search_params = update_filters(search_params, CLASSES_LIST)
    filters = parse_params(search_params)["filters_sqlalchemy_statement"]["objects"]

    return str(and_(*filters).compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


@pytest.mark.parametrize(
    "classifier, class_name",
    [
        ("lc_classifier_BHRF_forced_phot", "SNIa"),
        ("lc_classifier_BHRF_forced_phot_top", "Transient"),
        ("lc_classifier_BHRF_forced_phot_periodic", "LPV"),
    ],
)
def test_lc_classifier_lists_keep_objects_with_two_detections(classifier, class_name):
    assert "object.n_det >= 2" in object_filters_sql(classifier, class_name)


def test_lc_classifier_without_class_also_gets_the_filter():
    assert "object.n_det >= 2" in object_filters_sql("lc_classifier_BHRF_forced_phot", None)


def test_stamp_classifier_lists_keep_one_detection_objects():
    assert "n_det" not in object_filters_sql("stamp_classifier_2025_beta", "SN")


def test_user_n_det_range_is_kept_alongside():
    sql = object_filters_sql("lc_classifier_BHRF_forced_phot", "SNIa", n_det=[1, 10])

    assert "object.n_det >= 1 AND object.n_det <= 10" in sql
    assert "object.n_det >= 2" in sql


def test_lc_classifier_ids_are_the_five_bhrf_classifiers():
    # Changing this set changes which objects the lists return: see the warning in statements_sql.py.
    assert LC_CLASSIFIER_IDS == {5, 6, 7, 8, 9}
