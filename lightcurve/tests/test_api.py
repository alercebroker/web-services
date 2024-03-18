def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


def test_has_metrics(test_client):
    res = test_client.get("/")
    assert res.status_code == 200
    res = test_client.get("/metrics")
    assert res.status_code == 200
