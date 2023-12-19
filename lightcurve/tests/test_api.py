def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


def test_forced_photometry_from_ztf(
    psql_service, init_psql, test_client, mongo_service, init_mongo
):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "ztf"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 4


def test_forced_photometry_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "atlas"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_detections_without_survey_id_param(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_detections_from_ztf(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    insert_ztf_object(2, 5)
    res = test_client.get("/detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 3
    insert_atlas_objects(1,1)
    res = test_client.get("/detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 3

def test_non_detections_from_ztf(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_detections_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_detections_with_unknown_survey_id_param(test_client):
    res = test_client.get("/detections/oid1", params={"survey_id": "unknown"})
    assert "survey id not recognized unknown" in res.json()["detail"]


def test_lightcurve_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get("/lightcurve/oid2", params={"survey_id": "atlas"})
    assert res.status_code == 200
    json_res = res.json()
    # TODO: When a lightcurve contains only atlas detections and the user is
    # not authorized, the API will return None. Check if this will be the
    # intended behavior
    assert json_res is None


def test_lightcurve_from_atlas_without_results(
    mongo_service, init_mongo, test_client
):
    res = test_client.get("/lightcurve/oid100", params={"survey_id": "atlas"})
    assert res.status_code == 404


def test_lightcurve_from_ztf(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    res = test_client.get("/lightcurve/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    json_res = res.json()
    assert len(json_res["detections"]) == 3
    assert len(json_res["non_detections"]) == 3


def test_has_metrics(test_client):
    res = test_client.get("/")
    assert res.status_code == 200
    res = test_client.get("/metrics")
    assert res.status_code == 200


def test_lightcurve_multistream_only_in_mongo(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    res = test_client.get("/lightcurve/oid10")
    assert res.status_code == 200
    json_res = res.json()
    assert len(json_res["detections"]) == 1
    assert len(json_res["non_detections"]) == 1


def test_lightcurve_multistream_only_in_psql(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
):
    res = test_client.get("/lightcurve/oid20")
    assert res.status_code == 200
    json_res = res.json()
    assert len(json_res["detections"]) == 1
    assert len(json_res["non_detections"]) == 1
