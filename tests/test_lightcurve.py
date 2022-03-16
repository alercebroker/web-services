def test_get_lightcurve(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF1/lightcurve?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/lightcurve?survey_id=atlas")
    assert rv.status_code == 200


def test_get_lightcurve_not_found(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF2/lightcurve?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/lightcurve?survey_id=atlas")
    assert rv.status_code == 404


def test_get_detections(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF1/detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/detections?survey_id=atlas")
    assert rv.status_code == 200


def test_get_detections_not_found(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF2/detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/detections?survey_id=atlas")
    assert rv.status_code == 404


def test_get_non_detections(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF1/non_detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/non_detections?survey_id=atlas")
    assert rv.status_code == 200


def test_get_non_detections_not_found(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF2/non_detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/non_detections?survey_id=atlas")
    assert rv.status_code == 404

def test_bad_survey_id(mongo_service, psql_service, client):
    rv = client.get("objects/ZTF1/lightcurve")
    assert rv.status_code == 400

    rv = client.get("objects/ZTF1/lightcurve?survey_id=error")
    assert rv.status_code == 400
