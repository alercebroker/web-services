from fixtures import client


def test_get_lightcurve(psql_service, client):
    rv = client.get("objects/ZTF1/lightcurve")
    assert rv.status_code == 200


def test_get_lightcurve_not_found(psql_service, client):
    rv = client.get("objects/ZTF2/lightcurve")
    assert rv.status_code == 404


def test_get_detections(psql_service, client):
    rv = client.get("objects/ZTF1/detections")
    assert rv.status_code == 200


def test_get_detections_not_found(psql_service, client):
    rv = client.get("objects/ZTF2/detections")
    assert rv.status_code == 404


def test_get_non_detections(psql_service, client):
    rv = client.get("objects/ZTF1/non_detections")
    assert rv.status_code == 200


def test_get_non_detections_not_found(psql_service, client):
    rv = client.get("objects/ZTF2/non_detections")
    assert rv.status_code == 404
