"""The group panel of the light curve widget and the endpoint that serves the other objects' photometry."""

import json
import re

import pytest
from db_plugins.db.sql.models_pipeline import LsstDetection, ZtfDetection, ZtfObject
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from core.idmapper.idmapper import decode_masterid
from core.repository.association_models import (
    ASSOCIATION_SCHEMA,
    AssociationBase,
    AssociationMethod,
    ObjectAssociation,
    ObjectGroup,
)
from lightcurve_api.services import group_service

N_POINTS = 4


@pytest.fixture
def association_tables(db_setup, monkeypatch):
    monkeypatch.setenv("ASSOCIATION_SCHEMA", ASSOCIATION_SCHEMA)
    with db_setup.session() as session:
        session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {ASSOCIATION_SCHEMA}"))
        session.commit()
    AssociationBase.metadata.create_all(db_setup._engine)
    yield
    AssociationBase.metadata.drop_all(db_setup._engine)


@pytest.fixture
def group(db_setup, populate_database, association_tables):
    """A ZTF object and an LSST object in one group, and a second ZTF object nearby with a weak pair."""
    populate_database(N_POINTS)
    with db_setup.session() as session:
        ztf_a, ztf_c = session.execute(select(ZtfDetection.oid).distinct().limit(2)).scalars().all()
        lsst_x = session.execute(select(LsstDetection.oid).limit(1)).scalar_one()
        session.add(ZtfObject(oid=ztf_a, stellar=False, corrected=True))  # the widget looks it up
        session.add_all(
            [
                AssociationMethod(method_version=3, method_name="test", params={"groups": {"threshold": 0.95}}),
                ObjectGroup(oid=ztf_a, sid=0, group_id=7, group_version=2, method_version=3),
                ObjectGroup(oid=lsst_x, sid=1, group_id=7, group_version=2, method_version=3),
                ObjectAssociation(oid_a=ztf_a, sid_a=0, oid_b=lsst_x, sid_b=1, method_version=3, dist=0.3, score=0.99),
                ObjectAssociation(
                    oid_a=min(ztf_a, ztf_c),
                    sid_a=0,
                    oid_b=max(ztf_a, ztf_c),
                    sid_b=0,
                    method_version=3,
                    dist=2.0,
                    score=0.2,
                ),
            ]
        )
        session.commit()
    yield {"ztf_a": decode_masterid(ztf_a)[1], "ztf_c": decode_masterid(ztf_c)[1], "lsst_x": str(lsst_x)}
    with db_setup.session() as session:
        session.execute(text("DELETE FROM ztf_object"))
        session.commit()


def _embedded_group(html: str):
    match = re.search(r"^\s*group:\s*(.*),$", html, re.MULTILINE)
    return json.loads(match.group(1))


def test_widget_lists_members_and_nearby_objects(client: TestClient, group):
    response = client.get("/htmx/lightcurve", params={"oid": group["ztf_a"], "survey_id": "ztf"})

    assert response.status_code == 200
    embedded = _embedded_group(response.text)
    assert (embedded["group_id"], embedded["group_version"]) == (7, 2)
    assert [m["key"] for m in embedded["members"]] == [f"ztf:{group['ztf_a']}", f"lsst:{group['lsst_x']}"]
    assert [n["key"] for n in embedded["nearby"]] == [f"ztf:{group['ztf_c']}"]
    # The member is checked, the nearby object not, and both are disabled until the group switch is turned on
    assert re.search(rf'value="lsst:{group["lsst_x"]}"\s+checked\s+disabled>', response.text)
    assert re.search(rf'value="ztf:{group["ztf_c"]}"\s+disabled>', response.text)
    assert re.search(r'name="group.enabled" class="lc-sr"\s+>', response.text)  # rendered off
    # Every object carries its detections for the details line
    assert all(o["n_det"] is not None and o["firstmjd"] is not None for o in embedded["members"] + embedded["nearby"])


def test_widget_without_association_schema_has_no_group(client: TestClient, group, monkeypatch):
    monkeypatch.delenv("ASSOCIATION_SCHEMA")
    response = client.get("/htmx/lightcurve", params={"oid": group["ztf_a"], "survey_id": "ztf"})

    assert response.status_code == 200
    assert _embedded_group(response.text) is None
    assert "group.objects[]" not in response.text


def test_widget_still_renders_when_the_group_query_fails(client: TestClient, group, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("relation does not exist")

    monkeypatch.setattr(group_service, "get_group_info", broken)
    response = client.get("/htmx/lightcurve", params={"oid": group["ztf_a"], "survey_id": "ztf"})

    assert response.status_code == 200
    assert _embedded_group(response.text) is None


def test_group_photometry_tags_each_point_with_its_object(client: TestClient, group):
    objects = f"lsst:{group['lsst_x']},ztf:{group['ztf_c']}"
    response = client.get("/htmx/group_photometry", params={"objects": objects})

    assert response.status_code == 200
    body = response.json()
    by_object = {(d["survey_id"], d["oid"]) for d in body["detections"]}
    assert by_object == {("lsst", group["lsst_x"]), ("ztf", group["ztf_c"])}
    assert len(body["detections"]) == 2 * N_POINTS
    assert {f["oid"] for f in body["forced_photometry"]} == {group["lsst_x"], group["ztf_c"]}


def test_group_photometry_rejects_bad_objects(client: TestClient):
    response = client.get("/htmx/group_photometry", params={"objects": "atlas:1"})

    assert response.status_code == 400
