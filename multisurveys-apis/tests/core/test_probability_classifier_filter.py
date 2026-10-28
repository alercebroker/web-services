"""/probability answers 404 for an unknown classifier, also when there is only one classifier."""

import pytest

from app_client import client_for

OID = "170591527609303944"


@pytest.fixture
def client(db, monkeypatch):
    client = client_for("probability_api", db)
    from probability_api.routes import rest

    asked = []

    def fake_get_probability(master_id, classifiers, session_factory=None):
        asked.append(classifiers)
        return [{"classifier_name": name, "class_name": "SN", "probability": 1.0} for name in classifiers.values()]

    monkeypatch.setattr(rest, "get_classifiers", lambda session_factory=None: {1: "stamp_classifier_rubin_beta"})
    monkeypatch.setattr(rest, "get_probability", fake_get_probability)
    client.asked = asked
    yield client


def test_unknown_classifier_answers_404_with_a_single_classifier(client):
    response = client.get("/probability", params={"oid": OID, "survey_id": "lsst", "classifier": "foo"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Classifier 'foo' not found"}
    assert client.asked == []


def test_known_classifier_is_used(client):
    response = client.get(
        "/probability", params={"oid": OID, "survey_id": "lsst", "classifier": "stamp_classifier_rubin_beta"}
    )

    assert response.status_code == 200
    assert client.asked == [{1: "stamp_classifier_rubin_beta"}]
