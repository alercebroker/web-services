"""P3-4: list_objects' total is the number of matching rows when count=true, and null otherwise."""

import pytest
from db_plugins.db.sql.models_pipeline import Object, Probability, ZtfObject
from sqlalchemy import text

from app_client import client_for
from core.idmapper import idmapper

N_OBJECTS = 5
ZTF_NAMES = ["ZTF20aaaaaaa", "ZTF20aaaaaab", "ZTF20aaaaaac", "ZTF20aaaaaad", "ZTF20aaaaaae"]


@pytest.fixture
def client(db):
    rows = []
    for name in ZTF_NAMES[:N_OBJECTS]:
        oid = idmapper.catalog_oid_to_masterid("ZTF", name).item()
        rows.append(Object(oid=oid, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
    with db.session() as session:
        session.add_all(rows)
        session.commit()
        for obj in rows:
            session.add(ZtfObject(oid=obj.oid, stellar=False, corrected=False))
            session.add(
                Probability(
                    oid=obj.oid,
                    sid=0,
                    classifier_id=1,
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
        session.commit()


def test_total_counts_every_matching_row_when_asked(client):
    response = client.get("/list_objects", params={"survey": "ztf", "page_size": 2, "count": "true"})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    assert response.json()["total"] == N_OBJECTS


def test_total_is_null_without_count(client):
    response = client.get("/list_objects", params={"survey": "ztf", "page_size": 2})

    assert response.status_code == 200
    assert response.json()["total"] is None
    assert response.json()["has_next"] is True
