from email import headerregistry
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from api.resources.light_curve.models import get_magpsf, get_sigmapsf

def create_token(permisions, filters, secret_key):
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": permisions,
        "filters": filters,
    }
    encripted_token = jwt.encode(token, secret_key, algorithm="HS256")
    return encripted_token

def test_get_lightcurve(client):
    rv = client.get("objects/ZTF1/lightcurve?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/lightcurve?survey_id=atlas")
    assert rv.status_code == 200


def test_get_lightcurve_not_found(client):
    rv = client.get("objects/ZTF2/lightcurve?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/lightcurve?survey_id=atlas")
    assert rv.status_code == 404


def test_get_lightcurve_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ZTF1/lightcurve?survey_id=ztf", headers=headers)
    assert rv.status_code == 403


def test_get_lightcurve_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["basic_user"], ["filter_atlas_lightcurve"], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ATLAS1/lightcurve?survey_id=atlas", headers=headers)
    assert rv.status_code == 200
    assert rv.json == None


def test_get_detections(client):
    rv = client.get("objects/ZTF1/detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/detections?survey_id=atlas")
    assert rv.status_code == 200


def test_get_detections_not_found(client):
    rv = client.get("objects/ZTF2/detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/detections?survey_id=atlas")
    assert rv.status_code == 404


def test_get_detections_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ZTF1/detections?survey_id=ztf", headers=headers)
    assert rv.status_code == 403


def test_get_detections_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["basic_user"], ["filter_atlas_detections"], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ATLAS1/detections?survey_id=atlas", headers=headers)
    assert rv.status_code == 200
    assert rv.json == []


def test_get_non_detections(client):
    rv = client.get("objects/ZTF1/non_detections?survey_id=ztf")
    assert rv.status_code == 200

    rv = client.get("objects/ATLAS1/non_detections?survey_id=atlas")
    assert rv.status_code == 200


def test_get_non_detections_not_found(client):
    rv = client.get("objects/ZTF2/non_detections?survey_id=ztf")
    assert rv.status_code == 404

    rv = client.get("objects/ATLAS3/non_detections?survey_id=atlas")
    assert rv.status_code == 404


def test_get_non_detections_forbidden(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["useles_permission"], [], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ZTF1/non_detections?survey_id=ztf", headers=headers)
    assert rv.status_code == 403


def test_get_non_detections_filters(client, app):
    test_secret_key = app.config["RALIDATOR_SETTINGS"]["secret_key"]
    token = create_token(["basic_user"], ["filter_atlas_non_detections"], test_secret_key)
    headers = {
        'AUTH_TOKEN': token
    }
    rv = client.get("objects/ATLAS1/non_detections?survey_id=atlas", headers=headers)
    assert rv.status_code == 200
    assert rv.json == []


def test_bad_survey_id(client):
    rv = client.get("objects/ZTF1/lightcurve")
    assert rv.status_code == 400

    rv = client.get("objects/ZTF1/lightcurve?survey_id=error")
    assert rv.status_code == 400


def test_get_magpsf(populate_databases):
    app = populate_databases
    repo = app.container.lightcurve_package.detection_repository_factory("ztf")
    detection = repo.get("ZTF1", "ztf").unwrap()[0]
    magpsf = get_magpsf(detection)
    assert magpsf == 1

    repo = app.container.lightcurve_package.detection_repository_factory(
        "atlas"
    )
    detection = repo.get("ATLAS1", "atlas").unwrap()[0]
    magpsf = get_magpsf(detection)
    assert magpsf == 1

    with pytest.raises(Exception):
        detection = {}
        magpsf = get_magpsf(detection)


def test_get_sigmapsf(populate_databases):
    app = populate_databases
    repo = app.container.lightcurve_package.detection_repository_factory("ztf")
    detection = repo.get("ZTF1", "ztf").unwrap()[0]
    sigmapsf = get_sigmapsf(detection)
    assert sigmapsf == 1

    repo = app.container.lightcurve_package.detection_repository_factory(
        "atlas"
    )
    detection = repo.get("ATLAS1", "atlas").unwrap()[0]
    sigmapsf = get_sigmapsf(detection)
    assert sigmapsf == 1

    with pytest.raises(Exception):
        detection = {}
        sigmapsf = get_sigmapsf(detection)
