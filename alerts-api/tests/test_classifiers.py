def test_classifier_list(client):
    r = client.get("/classifiers/")
    # TODO Replace with actual assertion when classes are not hardcoded
    assert len(r.json) is not None


def test_classifier_classes(client):
    r = client.get("/classifiers/C1/1.0.0-test/classes")
    assert len(r.json) is not None
