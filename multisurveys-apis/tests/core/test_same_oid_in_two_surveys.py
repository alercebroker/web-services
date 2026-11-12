"""The common tables (object, probability) hold every survey, keyed by (oid, sid): the same numeric oid can be a
ZTF object and an LSST object. Each survey only sees its own."""

import pytest
from db_plugins.db.sql.models_pipeline import (
    Detection,
    LsstDetection,
    LsstDiaObject,
    Object,
    Probability,
    ZtfDetection,
    ZtfObject,
)
from sqlalchemy import text

from app_client import client_for
from core.idmapper import idmapper

NAME = "ZTF20aaaaazz"
OID = idmapper.catalog_oid_to_masterid("ZTF", NAME).item()
# survey -> (sid, meanra, a classifier of that survey)
SURVEYS = {"ztf": (0, 11.0, 4), "lsst": (1, 22.0, 3)}


@pytest.fixture
def db_with_both(db):
    with db.session() as session:
        for sid, meanra, _ in SURVEYS.values():
            session.add(Object(oid=OID, tid=sid, sid=sid, meanra=meanra, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        session.add(ZtfObject(oid=OID, stellar=False, corrected=False))
        session.add(LsstDiaObject(oid=OID, validityStartMjdTai=60000, ra=22.0, dec=10.0, nDiaSources=1))
        for sid, _, classifier_id in SURVEYS.values():
            session.add(
                Probability(
                    oid=OID,
                    sid=sid,
                    classifier_id=classifier_id,
                    classifier_version=1,
                    class_id=1,
                    probability=0.5,
                    ranking=1,
                    lastmjd=60010,
                )
            )
        session.commit()

    yield db

    with db.session() as session:
        session.execute(text("DELETE FROM probability WHERE oid = :o"), {"o": OID})
        session.execute(text("DELETE FROM ztf_object WHERE oid = :o"), {"o": OID})
        session.execute(text("DELETE FROM lsst_dia_object WHERE oid = :o"), {"o": OID})
        session.execute(text("DELETE FROM object WHERE oid = :o"), {"o": OID})
        session.commit()


@pytest.mark.parametrize("survey", SURVEYS)
def test_object_comes_from_its_survey(db_with_both, survey):
    sid, meanra, _ = SURVEYS[survey]
    response = client_for("object_api", db_with_both).get("/object", params={"oid": str(OID), "survey_id": survey})

    assert response.status_code == 200
    assert (response.json()["sid"], response.json()["meanra"]) == (sid, meanra)


@pytest.mark.parametrize("survey", SURVEYS)
def test_probabilities_come_from_their_survey(db_with_both, survey):
    _, _, classifier_id = SURVEYS[survey]
    names = {
        row["classifier_id"]: row["classifier_name"]
        for row in client_for("classifier_api", db_with_both).get("/classifiers").json()
    }
    response = client_for("probability_api", db_with_both).get(
        "/probability", params={"oid": str(OID), "survey_id": survey}
    )

    assert response.status_code == 200
    assert {row["classifier_name"] for row in response.json()} == {names[classifier_id]}


# The object each survey's conesearch must return: ZTF oids come back as ZTF names, LSST oids as numbers
OBJECT_IDS = {"ztf": NAME, "lsst": str(OID)}


@pytest.mark.parametrize("survey", SURVEYS)
def test_conesearch_by_oid_finds_only_its_survey(db_with_both, survey):
    _, meanra, _ = SURVEYS[survey]
    response = client_for("lightcurve_api", db_with_both).get(
        "/conesearch/objects_by_oid",
        params={"oid": str(OID), "survey_id": survey, "radius": 30, "neighbors": 10},
    )

    assert response.status_code == 200
    assert [(row["survey_id"], row["objectId"], row["ra"]) for row in response.json()] == [
        (survey, OBJECT_IDS[survey], meanra)
    ]


@pytest.fixture
def db_with_both_detections(db_with_both):
    """One detection per survey, with different measurement ids, so only the survey decides which one is read."""
    with db_with_both.session() as session:
        session.add(Detection(oid=OID, sid=0, measurement_id=1, mjd=60001, ra=11.0, dec=10.0, band=1))
        session.add(Detection(oid=OID, sid=1, measurement_id=2, mjd=60002, ra=22.0, dec=10.0, band=1))
        session.add(ZtfDetection(oid=OID, measurement_id=1, magpsf=18.0, sigmapsf=0.1))
        session.add(
            LsstDetection(
                oid=OID,
                sid=1,
                measurement_id=2,
                visit=1,
                detector=1,
                x=1,
                y=1,
                timeProcessedMjdTai=1,
                psfFlux=100.0,
                psfFluxErr=1.0,
                scienceFlux=100.0,
                scienceFluxErr=1.0,
                has_stamp=False,
            )
        )
        session.commit()

    yield db_with_both

    with db_with_both.session() as session:
        for table in ("ztf_detection", "lsst_detection", "detection"):
            session.execute(text(f"DELETE FROM {table} WHERE oid = :o"), {"o": OID})
        session.commit()


@pytest.mark.parametrize("survey", SURVEYS)
def test_conesearch_lightcurve_comes_from_its_survey(db_with_both_detections, survey):
    response = client_for("lightcurve_api", db_with_both_detections).get(
        "/conesearch/lightcurve_by_oid",
        params={"oid": str(OID), "survey_id": survey, "radius": 30, "neighbors": 10},
    )

    assert response.status_code == 200
    assert [row["survey_id"] for row in response.json()["detections"]] == [survey]
