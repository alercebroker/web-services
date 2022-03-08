def test_magstats(psql_service, client):
    r = client.get("objects/ZTF1/magstats")
    assert r.status_code == 200


def test_magstats_not_found(psql_service, client):
    r = client.get("objects/ZTF2/magstats")
    assert r.status_code == 404
