from fixtures import client 

def test_get_probabilities(client):
    r = client.get("objects/ZTF1/probabilities")
    assert r.status_code == 200
    assert isinstance(r.json, list)

def test_get_probabilities_not_found(client):
    r = client.get("objects/ZTF2/probabilities")
    assert r.status_code == 404
