"""P2-6: bad object-list filters answer 400 with a message, not 500 or a silently dropped filter."""

import pytest

from app_client import client_for

CLASSIFIER = "stamp_classifier_2025_beta"  # seeded with SN, AGN, VS, asteroid, bogus, satellite


@pytest.fixture
def client(db):
    # The test database is created with the classifiers and their classes already in it
    return client_for("object_api", db, raise_server_exceptions=False)


@pytest.mark.parametrize(
    "params, message",
    [
        ({"survey": "ztf", "classifier": "foo"}, "Classifier name 'foo' not found"),
        ({"survey": "ztf", "class_name": "asteroid"}, "class_name needs a classifier"),
        ({"survey": "ztf", "classifier": CLASSIFIER, "class_name": "SNIa"}, "Class 'SNIa' not found"),
        ({}, "survey is required"),
        ({"survey": "foo"}, "survey is required"),
    ],
)
def test_bad_list_filters_are_400(client, params, message):
    response = client.get("/list_objects", params=params)

    assert response.status_code == 400
    assert message in response.json()["detail"]


def test_good_filters_still_answer(client):
    response = client.get("/list_objects", params={"survey": "ztf", "classifier": CLASSIFIER, "class_name": "asteroid"})

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/htmx/list_objects", "/htmx/side_objects"])
def test_website_search_unknown_classifier_is_400(client, path):
    response = client.get(path, params={"survey": "ztf", "classifier": "foo"})

    assert response.status_code == 400
