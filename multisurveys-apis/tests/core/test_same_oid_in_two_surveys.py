"""The common tables (object, probability) hold every survey, keyed by (oid, sid): the same numeric oid can be a
ZTF object and an LSST object. Each survey only sees its own."""

import pytest
from db_plugins.db.sql.models_pipeline import LsstDiaObject, Object, Probability, ZtfObject
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
