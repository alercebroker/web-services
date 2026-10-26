"""P3-7b: for ZTF, the JSON answers carry the ZTF name as oid, not the internal numeric id."""

import pytest
from db_plugins.db.sql.models_pipeline import (
    Detection,
    ForcedPhotometry,
    Object,
    ZtfDetection,
    ZtfForcedPhotometry,
    ZtfNonDetection,
    ZtfObject,
)
from sqlalchemy import text

from app_client import client_for
from core.idmapper.idmapper import catalog_oid_to_masterid

NAME = "ZTF20aaelulu"
NUMBER = catalog_oid_to_masterid("ZTF", NAME).item()


@pytest.fixture
def ztf_object(db):
    with db.session() as session:
        session.add(Object(oid=NUMBER, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        session.add(ZtfObject(oid=NUMBER, stellar=False, corrected=False))
        session.add(Detection(oid=NUMBER, sid=0, measurement_id=1, mjd=60000, ra=10.0, dec=10.0, band=1))
        session.add(ZtfDetection(oid=NUMBER, measurement_id=1, magpsf=18.0, sigmapsf=0.1))
        session.add(ZtfNonDetection(oid=NUMBER, band=1, mjd=59990, diffmaglim=20.0))
        session.add(ForcedPhotometry(oid=NUMBER, sid=0, measurement_id=2, mjd=60005, ra=10.0, dec=10.0, band=1))
        session.add(
            ZtfForcedPhotometry(
                oid=NUMBER,
                measurement_id=2,
                mag=18.0,
                e_mag=0.1,
                isdiffpos=1,
                corrected=False,
                dubious=False,
                field=1,
                rcid=1,
                rfid=1,
                sciinpseeing=1,
                scibckgnd=1,
                scisigpix=1,
                magzpsci=1,
                magzpsciunc=1,
                magzpscirms=1,
                clrcoeff=1,
                clrcounc=1,
                exptime=1,
                adpctdif1=1,
                adpctdif2=1,
                diffmaglim=1,
                programid=1,
                procstatus="a",
                distnr=1,
                ranr=1,
                decnr=1,
                magnr=1,
                sigmagnr=1,
                chinr=1,
                sharpnr=1,
            )
        )
        session.commit()
    yield db
    with db.session() as session:
        session.execute(text("DELETE FROM ztf_object"))
        session.commit()


@pytest.mark.parametrize("oid", [NAME, str(NUMBER)])
def test_object_answers_the_ztf_name(ztf_object, oid):
    response = client_for("object_api", ztf_object).get("/object", params={"oid": oid, "survey_id": "ztf"})

    assert response.status_code == 200
    assert response.json()["oid"] == NAME


@pytest.mark.parametrize("path", ["/detections", "/non_detections", "/forced-photometry"])
@pytest.mark.parametrize("oid", [[NAME], [str(NUMBER)], [NAME, str(NUMBER)]])
def test_lightcurve_rows_answer_the_ztf_name(ztf_object, path, oid):
    response = client_for("lightcurve_api", ztf_object).get(path, params={"oid": oid, "survey_id": "ztf"})

    assert response.status_code == 200
    assert response.json()
    assert {row["oid"] for row in response.json()} == {NAME}


@pytest.mark.parametrize("oid", [[NAME], [str(NUMBER)]])
def test_full_lightcurve_answers_the_ztf_name(ztf_object, oid):
    response = client_for("lightcurve_api", ztf_object).get("/lightcurve", params={"oid": oid, "survey_id": "ztf"})

    assert response.status_code == 200
    for key in ("detections", "non_detections", "forced_photometry"):
        assert response.json()[key]
        assert {row["oid"] for row in response.json()[key]} == {NAME}
