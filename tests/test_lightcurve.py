import jwt
from datetime import datetime, timedelta, timezone
from conftest import models


def create_token(permisions, filters, secret_key):
    token = {
        "access": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": permisions,
        "filters": filters,
    }
    encripted_token = jwt.encode(token, secret_key, algorithm="HS256")
    return encripted_token


def test_get_lightcurve(client):
    rv = client.get("objects/AID_ZTF2/lightcurve?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/AID_ZTF2/lightcurve")
    assert rv.status_code == 200
    assert rv.json["detections"][0]["tid"].startswith("ZTF")

    rv = client.get("objects/AID_ATLAS1/lightcurve?survey_id=atlas")
    assert rv.status_code == 200


def test_get_lightcurve_not_found(client):
    rv = client.get("objects/ZTF2/lightcurve?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/lightcurve?survey_id=atlas")
    assert rv.status_code == 404


def test_get_lightcurve_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {"AUTH-TOKEN": token}
    rv = client.get("objects/ZTF1/lightcurve?survey_id=ztf", headers=headers)
    assert rv.status_code == 403


def test_get_lightcurve_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(
        ["basic_user"], ["filter_atlas_lightcurve"], test_secret_key
    )
    headers = {"AUTH-TOKEN": token}
    rv = client.get(
        "objects/AID_ATLAS1/lightcurve?survey_id=atlas", headers=headers
    )
    assert rv.status_code == 200
    assert rv.json is None


def test_get_detections(client):
    rv = client.get("objects/AID_ZTF2/detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/AID_ZTF2/detections")
    assert rv.status_code == 200
    assert rv.json[0]["tid"].startswith("ZTF")

    rv = client.get("objects/AID_ATLAS1/detections?survey_id=atlas")
    assert rv.status_code == 200


def test_sort_detections_by_date_descending(client, app):
    det = models.Detection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            candid="candid",
            mjd=0,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            e_mag=1,
            rfid=1,
            e_ra=1,
            e_dec=1,
            isdiffpos=1,
            magpsf_corr=1,
            sigmapsf_corr=1,
            sigmapsf_corr_ext=1,
            corrected=True,
            dubious=True,
            parent_candid=1234,
            has_stamp=True,
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
    app.container.mongo_db().query().get_or_create(det, model=models.Detection)
    rv = client.get("objects/AID_ZTF2/detections?order_by=mjd&order_mode=DESC")
    assert rv.status_code == 200
    assert len(rv.json) == 2
    assert rv.json[1]["oid"] == "ZTF22"
    assert rv.json[0]["oid"] == "ZTF2"


def test_sort_detections_by_date_ascending(client, app):
    det = models.Detection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            candid="candid",
            mjd=0,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            e_mag=1,
            rfid=1,
            e_ra=1,
            e_dec=1,
            isdiffpos=1,
            magpsf_corr=1,
            sigmapsf_corr=1,
            sigmapsf_corr_ext=1,
            corrected=True,
            dubious=True,
            parent_candid=1234,
            has_stamp=True,
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
    app.container.mongo_db().query().get_or_create(det, model=models.Detection)
    rv = client.get("objects/AID_ZTF2/detections?order_by=mjd&order_mode=ASC")
    assert rv.status_code == 200
    assert len(rv.json) == 2
    assert rv.json[0]["oid"] == "ZTF22"
    assert rv.json[1]["oid"] == "ZTF2"


def test_paginated_detections_result(client, app):
    det = models.Detection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            candid="candid",
            mjd=0,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            e_mag=1,
            rfid=1,
            e_ra=1,
            e_dec=1,
            isdiffpos=1,
            magpsf_corr=1,
            sigmapsf_corr=1,
            sigmapsf_corr_ext=1,
            corrected=True,
            dubious=True,
            parent_candid=1234,
            has_stamp=True,
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
    app.container.mongo_db().query().get_or_create(det, model=models.Detection)
    rv = client.get("objects/AID_ZTF2/detections?order_by=mjd&order_mode=ASC&page_size=1")
    assert rv.status_code == 200
    assert len(rv.json) == 1
    assert rv.json[0]["oid"] == "ZTF22"


def test_sort_non_detections_by_date_ascending(client, app):
    det = models.NonDetection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            mjd=0,
            diffmaglim=1,
            fid=1,
        )
    app.container.mongo_db().query().get_or_create(det, model=models.NonDetection)
    rv = client.get("objects/AID_ZTF2/non_detections?order_by=mjd&order_mode=ASC")
    assert rv.status_code == 200
    assert len(rv.json) == 2
    assert rv.json[0]["mjd"] == 0
    assert rv.json[1]["mjd"] == 1


def test_sort_non_detections_by_date_descending(client, app):
    det = models.NonDetection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            mjd=0,
            diffmaglim=1,
            fid=1,
        )
    app.container.mongo_db().query().get_or_create(det, model=models.NonDetection)
    rv = client.get("objects/AID_ZTF2/non_detections?order_by=mjd&order_mode=DESC")
    assert rv.status_code == 200
    assert len(rv.json) == 2
    assert rv.json[1]["mjd"] == 0
    assert rv.json[0]["mjd"] == 1


def test_paginated_non_detections_result(client, app):
    det = models.NonDetection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF22",
            mjd=0,
            diffmaglim=1,
            fid=1,
        )
    app.container.mongo_db().query().get_or_create(det, model=models.NonDetection)
    rv = client.get("objects/AID_ZTF2/non_detections?order_by=mjd&order_mode=ASC&page_size=1")
    assert rv.status_code == 200
    assert len(rv.json) == 1
    assert rv.json[0]["mjd"] == 0


def test_get_detections_not_found(client):
    rv = client.get("objects/AID_ZTF3/detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/AID_ATLAS3/detections?survey_id=atlas")
    assert rv.status_code == 404


def test_get_detections_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {"AUTH-TOKEN": token}
    rv = client.get("objects/ZTF1/detections?survey_id=ztf", headers=headers)
    assert rv.status_code == 403


def test_get_detections_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], test_secret_key
    )
    headers = {"AUTH-TOKEN": token}
    rv = client.get(
        "objects/AID_ATLAS1/detections?survey_id=atlas", headers=headers
    )
    assert rv.status_code == 200
    assert rv.json == []


def test_get_non_detections(client):
    rv = client.get("objects/AID_ZTF2/non_detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/AID_ZTF2/non_detections")
    assert rv.status_code == 200
    assert rv.json[0]["tid"].startswith("ZTF")

    rv = client.get("objects/AID_ATLAS1/non_detections?survey_id=atlas")
    assert rv.status_code == 200


def test_get_non_detections_not_found(client):
    rv = client.get("objects/ZTF2/non_detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/non_detections?survey_id=atlas")
    assert rv.status_code == 404


def test_get_non_detections_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {"AUTH-TOKEN": token}
    rv = client.get(
        "objects/ZTF1/non_detections?survey_id=ztf", headers=headers
    )
    assert rv.status_code == 403


def test_get_non_detections_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["SECRET_KEY"]
    token = create_token(
        ["basic_user"], ["filter_atlas_non_detections"], test_secret_key
    )
    headers = {"AUTH-TOKEN": token}
    rv = client.get(
        "objects/AID_ATLAS1/non_detections?survey_id=atlas", headers=headers
    )
    assert rv.status_code == 200
    assert rv.json == []


def test_bad_survey_id(client):
    rv = client.get("objects/ZTF1/lightcurve?survey_id=error")
    assert rv.status_code == 400
