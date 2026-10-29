"""/probability with a classifier: unknown names answer 404, and a name is looked up in the object's survey."""

import pytest

from app_client import client_for

LSST_OID = "170591527609303944"
ZTF_OID = "ZTF18abbrrty"


@pytest.fixture
def client(db, monkeypatch):
    client = client_for("probability_api", db)
    from probability_api.routes import rest

    asked = []

    def fake_get_probability(master_id, classifiers, session_factory=None):
        asked.append(classifiers)
        return [{"classifier_name": name, "class_name": "SN", "probability": 1.0} for name in classifiers.values()]

    monkeypatch.setattr(rest, "get_probability", fake_get_probability)
    client.asked = asked
    yield client


@pytest.mark.parametrize(
    "params",
    [
        {"oid": LSST_OID, "survey_id": "lsst", "classifier": "foo"},
        # a ZTF classifier asked for an LSST object
        {"oid": LSST_OID, "survey_id": "lsst", "classifier": "stamp_classifier_ztf"},
    ],
)
def test_a_classifier_the_survey_doesnt_have_answers_404(client, params):
    response = client.get("/probability", params=params)

    assert response.status_code == 404
    assert response.json() == {"detail": f"Classifier '{params['classifier']}' not found"}
    assert client.asked == []


def test_known_classifier_is_used(client):
    name = "stamp_classifier_rubin_beta_20260421"
    response = client.get("/probability", params={"oid": LSST_OID, "survey_id": "lsst", "classifier": name})

    assert response.status_code == 200
    assert client.asked == [{3: name}]


@pytest.mark.parametrize(
    "params, classifier_id",
    [
        ({"oid": ZTF_OID, "survey_id": "ztf"}, 4),
        ({"oid": ZTF_OID}, 4),  # without a survey, the oid is a ZTF one
        ({"oid": LSST_OID, "survey_id": "lsst"}, 99),
    ],
)
def test_a_name_in_both_surveys_is_taken_from_the_objects_survey(client, same_name_for_lsst, params, classifier_id):
    response = client.get("/probability", params={**params, "classifier": "stamp_classifier_ztf"})

    assert response.status_code == 200
    assert client.asked == [{classifier_id: "stamp_classifier_ztf"}]
