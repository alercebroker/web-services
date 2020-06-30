from fixtures import client 

def test_magstats(client):
    r = client.get("objects/ZTF1/magstats")
    assert r.status_code == 200

def test_magstats_not_found(client):
    r = client.get("objects/ZTF2/magstats")
    assert r.status_code == 404