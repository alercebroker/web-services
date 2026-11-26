"""The group panel of the light curve widget and the endpoint that serves the other objects' photometry."""

import json
import re

import pytest
from db_plugins.db.sql.models_pipeline import LsstDetection, ZtfDetection, ZtfObject
from fastapi.testclient import TestClient
from sqlalchemy import event, select, text

from core import association as association_setting
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
    monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", ASSOCIATION_SCHEMA)
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


def test_the_group_panel_costs_one_statement(client: TestClient, group, db_setup, monkeypatch):
    """Each query is a round trip to a distant database in production, so the panel must stay one statement."""
    statements = []
    listener = lambda *args: statements.append(args[2])  # noqa: E731  (args[2] is the SQL)
    params = {"oid": group["ztf_a"], "survey_id": "ztf"}
    event.listen(db_setup._engine, "before_cursor_execute", listener)
    try:
        client.get("/htmx/lightcurve", params=params)
        with_panel = len(statements)
        statements.clear()
        monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", None)
        client.get("/htmx/lightcurve", params=params)
        without_panel = len(statements)
    finally:
        event.remove(db_setup._engine, "before_cursor_execute", listener)

    assert with_panel - without_panel == 1


def test_widget_without_association_schema_has_no_group(client: TestClient, group, monkeypatch):
    monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", None)
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


def test_group_photometry_times_are_barycentric(client: TestClient, group):
    # Every point gets its BJD_TDB for the fold, at most the Earth-orbit delay (8.3 min) plus the clock and
    # exposure offsets (about a minute) away from its observed time
    objects = f"lsst:{group['lsst_x']},ztf:{group['ztf_c']}"
    response = client.get("/htmx/group_photometry", params={"objects": objects, "ra": 10.0, "dec": 20.0})

    points = response.json()["detections"] + response.json()["forced_photometry"]
    assert points
    assert all(abs(p["bjd_tdb"] - p["mjd"]) * 86400 < 600 for p in points)


def test_periodogram_searches_the_drawn_objects_too(client: TestClient, group, monkeypatch):
    # The viewed object's own detections and those of the objects named in `objects`, the viewed one only once
    from lightcurve_api.models.periodogram import Periodogram
    from lightcurve_api.services.period import service as period_service

    searched = []
    to_dataframe = period_service.detections2dataframe
    monkeypatch.setattr(
        period_service, "detections2dataframe", lambda dets, times=None: searched.append(dets) or to_dataframe(dets)
    )
    empty = Periodogram(periods=[], scores=[], best_periods=[], best_periods_index=[])
    monkeypatch.setattr(period_service.PeriodogramComputer, "compute", lambda self, df: empty)

    params = {"oid": group["ztf_a"], "survey_id": "ztf"}  # no ra/dec: the mean of the detections
    alone = client.get("/htmx/periodogram", params=params)
    objects = f"lsst:{group['lsst_x']},ztf:{group['ztf_a']}"
    with_member = client.get("/htmx/periodogram", params={**params, "objects": objects})

    assert alone.status_code == with_member.status_code == 200
    own, combined = searched
    assert own and {d.survey_id.lower() for d in own} == {"ztf"}
    members = [d for d in combined if d.survey_id.lower() == "lsst"]
    assert {d.oid for d in members} == {int(group["lsst_x"])}
    assert len(combined) == len(own) + len(members) == len(own) + N_POINTS


def test_periodogram_rejects_bad_objects(client: TestClient):
    response = client.get("/htmx/periodogram", params={"oid": "ZTF18abvkqpo", "survey_id": "ztf", "objects": "atlas:1"})

    assert response.status_code == 400


def test_group_photometry_rejects_bad_objects(client: TestClient):
    response = client.get("/htmx/group_photometry", params={"objects": "atlas:1"})

    assert response.status_code == 400


def test_aladin_panel_gets_the_other_members_at_their_mean_position(db_setup, group, monkeypatch):
    """The Aladin API marks the group too (aladin_api/services/aladin_services.py); it shares these tables."""
    from aladin_api.services.aladin_services import get_group_objects
    from db_plugins.db.sql.models_pipeline import Object

    from core.idmapper.idmapper import parse_oid

    lsst_x = int(group["lsst_x"])
    with db_setup.session() as session:
        lsst_row = session.execute(select(Object).where(Object.oid == lsst_x, Object.sid == 1)).scalar_one()

    from_ztf = get_group_objects(db_setup.session, parse_oid("ztf", group["ztf_a"]), 0)
    from_lsst = get_group_objects(db_setup.session, lsst_x, 1)

    assert from_ztf == [
        {"oid": group["lsst_x"], "sid": 1, "meanra": lsst_row.meanra, "meandec": lsst_row.meandec, "associated": True}
    ]
    assert [obj["oid"] for obj in from_lsst] == [group["ztf_a"]]  # the ZTF name, not the internal number

    monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", None)
    assert get_group_objects(db_setup.session, lsst_x, 1) == []
