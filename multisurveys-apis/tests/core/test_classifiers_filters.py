"""P3-5: /classifiers filters by classifier_name (it answered 500) and by survey_id (it was ignored)."""

import pytest
from sqlalchemy import text

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


@pytest.mark.parametrize(
    "params, status",
    [
        ({"classifier_name": "foo"}, 404),
        ({"survey_id": "foo"}, 400),
        ({"classifier_name": "foo", "survey_id": "atlas"}, 400),
    ],
)
def test_errors(client, params, status):
    assert client.get("/classifiers", params=params).status_code == status


@pytest.fixture
def same_name_for_lsst(db):
    """stamp_classifier_ztf registered a second time, for LSST, with the same version and other classes."""
    with db.session() as session:
        version = session.execute(
            text("SELECT classifier_version FROM classifier WHERE classifier_name = 'stamp_classifier_ztf'")
        ).scalar_one()
        session.execute(
            text(
                "INSERT INTO classifier (classifier_id, classifier_name, classifier_version, tid) "
                "VALUES (99, 'stamp_classifier_ztf', :version, 1)"
            ),
            {"version": version},
        )
        session.execute(
            text(
                'INSERT INTO taxonomy (class_id, class_name, "order", classifier_id) '
                "VALUES (0, 'only_lsst_a', 0, 99), (1, 'only_lsst_b', 1, 99)"
            )
        )
        session.commit()
    yield version
    with db.session() as session:
        session.execute(text("DELETE FROM taxonomy WHERE classifier_id = 99"))
        session.execute(text("DELETE FROM classifier WHERE classifier_id = 99"))
        session.commit()


def test_classifiers_with_the_same_name_are_listed_apart(client, same_name_for_lsst):
    response = client.get("/classifiers", params={"classifier_name": "stamp_classifier_ztf"})

    by_survey = {c["survey_id"]: c for c in response.json()}
    assert set(by_survey) == {0, 1}
    assert by_survey[1]["classes"] == ["only_lsst_a", "only_lsst_b"]
    assert "only_lsst_a" not in by_survey[0]["classes"]


def test_a_classifier_is_found_by_survey_even_if_its_name_exists_in_another(client, same_name_for_lsst):
    response = client.get("/classifiers", params={"survey_id": "lsst"})

    assert "stamp_classifier_ztf" in names(response)


def test_classes_of_a_name_and_version_in_two_surveys(client, same_name_for_lsst):
    params = {"classifier_name": "stamp_classifier_ztf", "classifier_version": same_name_for_lsst}

    assert client.get("/classes", params=params).status_code == 200
    lsst = client.get("/classes", params={**params, "survey_id": "lsst"})
    assert lsst.json() == [{"name": "only_lsst_a"}, {"name": "only_lsst_b"}]
    assert client.get("/classes", params={**params, "survey_id": "atlas"}).status_code == 400
