import pytest
from api.resources.light_curve.models import get_magpsf, get_sigmapsf


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
