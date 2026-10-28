"""A ZTF point without a corrected magnitude answers null in the JSON, not 0.

The models keep their 0 (the lightcurve plot relies on it); only the JSON answer changes.
"""

import importlib

import pytest
from db_plugins.db.sql.models_pipeline import Detection, Object, ZtfDetection
from fastapi.testclient import TestClient

from core.idmapper.idmapper import catalog_oid_to_masterid
from lightcurve_api.models.detections import ztfDetection
from lightcurve_api.models.force_photometry import ZtfForcedPhotometry
from lightcurve_api.routes.json.missing_values import json_rows

NAME = "ZTF20aaelulu"
NUMBER = catalog_oid_to_masterid("ZTF", NAME).item()


@pytest.fixture
def client(db):
    with db.session() as session:
        session.add(Object(oid=NUMBER, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        # (magpsf_corr, sigmapsf_corr, sigmapsf_corr_ext): uncorrected, corrected, corrected with an error the
        # pipeline couldn't compute, and the historical uncorrected form
        rows = [(None, None, None), (18.1, 0.05, 0.06), (18.2, 100.0, 0.07), (None, 100.0, 0.0)]
        for i, (corr, sigma, sigma_ext) in enumerate(rows):
            session.add(Detection(oid=NUMBER, sid=0, measurement_id=i, mjd=60000 + i, ra=10.0, dec=10.0, band=1))
            session.add(
                ZtfDetection(
                    oid=NUMBER,
                    measurement_id=i,
                    magpsf=18.0,
                    sigmapsf=0.1,
                    magpsf_corr=corr,
                    sigmapsf_corr=sigma,
                    sigmapsf_corr_ext=sigma_ext,
                    corrected=corr is not None,
                )
            )
        session.commit()

    # Imported here: the app builds its engine at import, from the env the db fixture sets
    app = importlib.import_module("lightcurve_api.api").app
    return TestClient(app)


@pytest.mark.parametrize("path", ["/detections", "/lightcurve"])
def test_uncorrected_ztf_detection_is_null_and_corrected_one_keeps_its_value(client, path):
    response = client.get(path, params={"survey_id": "ztf", "oid": [NAME]})
    rows = response.json() if path == "/detections" else response.json()["detections"]
    by_id = {row["measurement_id"]: row for row in rows}

    assert response.status_code == 200
    assert (by_id[0]["magpsf_corr"], by_id[0]["sigmapsf_corr"], by_id[0]["sigmapsf_corr_ext"]) == (None, None, None)
    assert (by_id[1]["magpsf_corr"], by_id[1]["sigmapsf_corr"], by_id[1]["sigmapsf_corr_ext"]) == (18.1, 0.05, 0.06)


@pytest.mark.parametrize("path", ["/detections", "/lightcurve"])
def test_values_the_pipeline_could_not_compute_are_null(client, path):
    response = client.get(path, params={"survey_id": "ztf", "oid": [NAME]})
    rows = response.json() if path == "/detections" else response.json()["detections"]
    by_id = {row["measurement_id"]: row for row in rows}

    assert (by_id[2]["magpsf_corr"], by_id[2]["sigmapsf_corr"], by_id[2]["sigmapsf_corr_ext"]) == (18.2, None, 0.07)
    assert (by_id[3]["magpsf_corr"], by_id[3]["sigmapsf_corr"], by_id[3]["sigmapsf_corr_ext"]) == (None, None, None)


def test_json_rows_nulls_forced_photometry_that_could_not_be_measured():
    ztf = {"oid": 36029005864454959, "survey_id": "ztf", "mag": 100.0, "e_mag": 100.0, "mag_corr": 100.0}

    assert json_rows([ztf]) == [
        {"oid": "ZTF26aboikah", "survey_id": "ztf", "mag": None, "e_mag": None, "mag_corr": None}
    ]


@pytest.mark.parametrize("survey_id", ["ztf", "lsst"])
def test_json_rows_nulls_floats_json_cannot_carry(survey_id):
    row = {"oid": 36029005864454959, "survey_id": survey_id, "psfFlux": float("nan"), "magpsf": float("inf")}

    item = json_rows([row])[0]

    assert (item["psfFlux"], item["magpsf"]) == (None, None)


@pytest.mark.parametrize("model, field", [(ztfDetection, "magpsf_corr"), (ZtfForcedPhotometry, "mag_corr")])
@pytest.mark.parametrize("value, has_total", [(0, False), (18.1, True), (100.0, False)])
def test_only_computed_corrected_magnitudes_are_plotted_as_total(model, field, value, has_total):
    assert model.model_construct(**{field: value}).has_total() is has_total


def test_json_rows_nulls_ztf_forced_photometry_and_leaves_lsst_alone():
    ztf = {
        "oid": 36029005864454959,
        "survey_id": "ztf",
        "mag": 18.0,
        "mag_corr": 0,
        "e_mag_corr": 0,
        "e_mag_corr_ext": 0,
    }
    lsst = {"oid": 170591527609303944, "survey_id": "lsst", "psfFlux": 0}

    assert json_rows([ztf, lsst]) == [
        {
            "oid": "ZTF26aboikah",
            "survey_id": "ztf",
            "mag": 18.0,
            "mag_corr": None,
            "e_mag_corr": None,
            "e_mag_corr_ext": None,
        },
        {"oid": 170591527609303944, "survey_id": "lsst", "psfFlux": 0},
    ]
