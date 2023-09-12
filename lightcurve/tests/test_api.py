def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


def test_detections_without_survey_id_param(
    psql_service, init_psql, test_client
):
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_ztf(psql_service, init_psql, test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_non_detections_from_ztf(psql_service, init_psql, test_client):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_detections_with_unknown_survey_id_param(test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "unknown"})
    assert "survey id not recognized unknown" in res.json()["detail"]


def test_lightcurve_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get("/lightcurve/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    json_res = res.json()
    # TODO: When a lightcurve contains only atlas detections and the user is
    # not authorized, the API will return None. Check if this will be the
    # intended behavior
    assert json_res is None


def test_lightcurve_from_ztf(psql_service, init_psql, test_client):
    res = test_client.get("/lightcurve/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    json_res = res.json()
    assert len(json_res["detections"]) == 2
    assert len(json_res["non_detections"]) == 2


def test_has_metrics(test_client):
    res = test_client.get("/")
    assert res.status_code == 200
    res = test_client.get("/metrics")
    assert res.status_code == 200
