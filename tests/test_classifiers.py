from fixtures import client, db, BaseQuery, models
from unittest.mock import patch


def test_classifier_list(client):
    r = client.get("/classifiers/")
    # TODO Replace with actual assertion when classes are not hardcoded
    assert len(r.json) is not None


def test_classifier_classes(client):
    r = client.get("/classifiers/Stamp/classes")
    assert len(r.json) is not None
