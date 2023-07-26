import pytest


def test_root(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    res = test_client.get("/")
    assert res.status_code == 200


def test_detections_without_survey_id_param(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_ztf(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    res = test_client.get("/detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_non_detections_from_ztf(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_from_atlas(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    res = test_client.get("/detections/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_detections_with_unknown_survey_id_param(
    psql_service, mongo_service, psql_database, mongo_database, test_client
):
    with pytest.raises(Exception, match="survey id not recognized unknown"):
        test_client.get("/detections/oid1", params={"survey_id": "unknown"})
