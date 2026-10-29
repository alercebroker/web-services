"""The survey is read in any case, and an uppercase survey still filters by survey."""

import pytest
from db_plugins.db.sql.models_pipeline import LsstDiaObject, Object, Probability, ZtfObject
from sqlalchemy import text

from app_client import client_for
from core.idmapper import idmapper

ZTF_NAME = "ZTF20aaaaaaz"
LSST_OID = 170433140619739440


@pytest.fixture
def client(db):
    ztf_oid = idmapper.catalog_oid_to_masterid("ZTF", ZTF_NAME).item()
    with db.session() as session:
        session.add_all(
            [
                Object(oid=ztf_oid, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010),
                Object(oid=LSST_OID, tid=1, sid=1, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010),
            ]
        )
        session.commit()
        session.add(ZtfObject(oid=ztf_oid, stellar=False, corrected=False))
        session.add(LsstDiaObject(oid=LSST_OID, validityStartMjdTai=60000, ra=10.0, dec=10.0, nDiaSources=1))
        for oid, sid, classifier_id in ((ztf_oid, 0, 4), (LSST_OID, 1, 3)):
            session.add(
                Probability(
                    oid=oid,
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

    yield client_for("object_api", db)

    with db.session() as session:
        session.execute(text("DELETE FROM probability"))
        session.execute(text("DELETE FROM ztf_object"))
        session.execute(text("DELETE FROM lsst_dia_object WHERE oid = :l"), {"l": LSST_OID})
        session.execute(text("DELETE FROM object WHERE oid IN (:z, :l)"), {"z": ztf_oid, "l": LSST_OID})
        session.commit()


@pytest.mark.parametrize("survey, oid", [("ztf", ZTF_NAME), ("lsst", LSST_OID)])
@pytest.mark.parametrize("sent", [str.lower, str.upper, str.title])
def test_list_objects_filters_by_survey_in_any_case(client, survey, oid, sent):
    response = client.get("/list_objects", params={"survey": sent(survey)})

    assert response.status_code == 200
    assert [item["oid"] for item in response.json()["items"]] == [oid]


@pytest.mark.parametrize("path", ["/htmx/list_objects", "/htmx/side_objects"])
def test_website_search_filters_by_survey_in_any_case(client, path):
    lower = client.get(path, params={"survey": "ztf"})
    upper = client.get(path, params={"survey": "ZTF"})

    assert upper.status_code == 200
    assert upper.text == lower.text
    assert ZTF_NAME in upper.text
    assert str(LSST_OID) not in upper.text


@pytest.mark.parametrize("survey", ["ZTF", "Ztf"])
def test_object_takes_the_survey_in_any_case(client, survey):
    response = client.get("/object", params={"oid": ZTF_NAME, "survey_id": survey})

    assert response.status_code == 200
    assert response.json()["oid"] == ZTF_NAME
