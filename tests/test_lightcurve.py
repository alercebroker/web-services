import jwt
from datetime import datetime, timedelta, timezone


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
