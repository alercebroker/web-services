def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


def test_detections_without_survey_id_param(
    psql_service, psql_database, test_client
):
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_ztf(psql_service, psql_database, test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_non_detections_from_ztf(psql_service, psql_database, test_client):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_atlas(mongo_service, mongo_database, test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_with_unknown_survey_id_param(test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "unknown"})
    assert "survey id not recognized unknown" in res.json()["detail"]


def test_lightcurve_from_atlas(mongo_service, mongo_database, test_client):
    res = test_client.get("/lightcurve/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 2
    assert len(res.json()["non_detections"]) == 0


def test_lightcurve_from_ztf(psql_service, psql_database, test_client):
    res = test_client.get("/lightcurve/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 2
    assert len(res.json()["non_detections"]) == 2
