"""A ZTF point without a corrected magnitude answers null in the JSON and is empty in the CSV, not 0.

The models keep the NULL as None; has_total() tells the plot which points have a corrected magnitude.
"""

import csv
import importlib
import io
import zipfile

import pytest
from db_plugins.db.sql.models_pipeline import Detection, Object, ZtfDetection, ZtfObject
from sqlalchemy import text
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
        session.add(ZtfObject(oid=NUMBER, stellar=False, corrected=True))  # the lightcurve card looks it up
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
    yield TestClient(app)

    with db.session() as session:
        session.execute(text("DELETE FROM ztf_object WHERE oid = :o"), {"o": NUMBER})
        session.commit()


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
@pytest.mark.parametrize("value, has_total", [(None, False), (0, False), (18.1, True), (100.0, False)])
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


def test_the_lightcurve_card_plots_uncorrected_points_without_a_total(client):
    response = client.get("/htmx/lightcurve", params={"survey_id": "ztf", "oid": NAME})

    assert response.status_code == 200


def test_csv_download_leaves_missing_corrected_values_empty(client):
    response = client.get("/htmx/download", params={"survey_id": "ztf", "oid": NAME})

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        name = next(n for n in archive.namelist() if "detection" in n and "non" not in n)
        rows = {row["measurement_id"]: row for row in csv.DictReader(io.StringIO(archive.read(name).decode()))}
    assert (rows["0"]["magpsf_corr"], rows["0"]["sigmapsf_corr"], rows["0"]["sigmapsf_corr_ext"]) == ("", "", "")
    assert rows["1"]["magpsf_corr"] == "18.1"


@pytest.mark.parametrize(
    "fields",
    [
        {"magpsf_corr": None, "sigmapsf_corr": None, "sigmapsf_corr_ext": None},
        # corrected, but without its error: plotted without an error bar
        {"magpsf_corr": 18.1, "sigmapsf_corr": 0.05, "sigmapsf_corr_ext": None},
    ],
)
def test_plot_variants_with_missing_corrected_values(fields):
    detection = ztfDetection.model_construct(magpsf=18.0, sigmapsf=0.1, isdiffpos=1, **fields)

    variants = detection.plot_variants()

    assert variants["mag_diff"]["y"] == 18.0
    if fields["magpsf_corr"] is None:
        assert variants["mag_total"] is None and variants["flux_total"] is None
    else:
        assert variants["mag_total"] == {"y": 18.1, "err": 0.0, "sign": "+"}
