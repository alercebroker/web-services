def test_magstats(client):
    r = client.get("objects/ALERCE1/magstats")
    assert r.status_code == 200


def test_magstats_not_found(client):
    r = client.get("objects/ALERCE2/magstats")
    assert r.status_code == 404
