from test_utils import create_token
import os


def test_get_multistream_lightcurve_all_surveys_unauthenticated(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # unauthenticated requests filter all atlas
    res = test_client.get("/lightcurve/oid1?survey_id=all")
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 1
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 1
    res = test_client.get("/lightcurve/oid3?survey_id=all")
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 1
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 1


def test_get_multistream_lightcurve_all_surveys_forbidden(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["forbidden"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/lightcurve/oid1?survey_id=all", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/lightcurve/oid3?survey_id=all", headers=headers)
    assert res.status_code == 403


def test_get_multistream_lightcurve_all_surveys_authenticated_without_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/lightcurve/oid1?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 2
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 2
    res = test_client.get("/lightcurve/oid3?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 2
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 2


def test_get_multistream_lightcurve_all_surveys_authenticated_with_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_lightcurve"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/lightcurve/oid1?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 1
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 1
    res = test_client.get("/lightcurve/oid3?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["detections"]) == 1
    assert len(res.json()["non_detections"]) == 2
    assert len(res.json()["forced_photometry"]) == 1


def test_get_detections_from_unknown_survey(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
):
    res = test_client.get("/lightcurve/oid1?survey_id=unknown")
    assert res.status_code == 400
