"""P1-4, JSON half: a ZTF point without a corrected magnitude answers null in the JSON, not 0.

The models keep their 0 (the lightcurve plot relies on it); only the JSON answer changes.
"""

import importlib

import pytest
from db_plugins.db.sql.models_pipeline import Detection, Object, ZtfDetection
from fastapi.testclient import TestClient

from core.idmapper.idmapper import catalog_oid_to_masterid
from lightcurve_api.routes.json.missing_values import json_rows

NAME = "ZTF20aaelulu"
NUMBER = catalog_oid_to_masterid("ZTF", NAME).item()


@pytest.fixture
def client(db):
    with db.session() as session:
        session.add(Object(oid=NUMBER, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        for i, corr in enumerate([None, 18.1]):  # one uncorrected point, one corrected
            session.add(Detection(oid=NUMBER, sid=0, measurement_id=i, mjd=60000 + i, ra=10.0, dec=10.0, band=1))
            session.add(
                ZtfDetection(
                    oid=NUMBER,
                    measurement_id=i,
                    magpsf=18.0,
                    sigmapsf=0.1,
                    magpsf_corr=corr,
                    sigmapsf_corr=None if corr is None else 0.05,
                    sigmapsf_corr_ext=None if corr is None else 0.06,
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


def test_json_rows_nulls_ztf_forced_photometry_and_leaves_lsst_alone():
    ztf = {"survey_id": "ztf", "mag": 18.0, "mag_corr": 0, "e_mag_corr": 0, "e_mag_corr_ext": 0}
    lsst = {"survey_id": "lsst", "psfFlux": 0}

    assert json_rows([ztf, lsst]) == [
        {"survey_id": "ztf", "mag": 18.0, "mag_corr": None, "e_mag_corr": None, "e_mag_corr_ext": None},
        {"survey_id": "lsst", "psfFlux": 0},
    ]
