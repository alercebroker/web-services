"""P3-5: /classifiers filters by classifier_name (it answered 500) and by survey_id (it was ignored)."""

import pytest

from app_client import client_for

# Seeded by the test database: (name, tid), tid 0 = ZTF, 1 = LSST
ZTF_CLASSIFIERS = {"stamp_classifier_2025_beta", "stamp_classifier_ztf"}
LSST_CLASSIFIERS = {"stamp_classifier_rubin", "stamp_classifier_rubin_beta_20260421"}


@pytest.fixture
def client(db):
    return client_for("classifier_api", db, raise_server_exceptions=False)


def names(response):
    return {classifier["classifier_name"] for classifier in response.json()}


def test_by_name_is_a_list_with_its_classes(client):
    response = client.get("/classifiers", params={"classifier_name": "stamp_classifier_2025_beta"})

    assert response.status_code == 200
    assert names(response) == {"stamp_classifier_2025_beta"}
    assert response.json()[0]["classes"] == ["SN", "AGN", "VS", "asteroid", "bogus", "satellite"]


@pytest.mark.parametrize(
    "params, expected",
    [
        ({}, ZTF_CLASSIFIERS | LSST_CLASSIFIERS),
        ({"survey_id": "ztf"}, ZTF_CLASSIFIERS),
        ({"survey_id": "lsst"}, LSST_CLASSIFIERS),
        ({"survey_id": "lsst", "classifier_name": "stamp_classifier_ztf"}, set()),
    ],
)
def test_filters(client, params, expected):
    response = client.get("/classifiers", params=params)

    assert response.status_code == 200
    assert names(response) == expected


@pytest.mark.parametrize("params, status", [({"classifier_name": "foo"}, 404), ({"survey_id": "foo"}, 400)])
def test_errors(client, params, status):
    assert client.get("/classifiers", params=params).status_code == status
