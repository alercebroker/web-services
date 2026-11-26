"""The website's results table shows each object's counterparts ("Also seen as") where association data is set."""

import pytest
from db_plugins.db.sql.models_pipeline import Object, Probability, ZtfObject
from sqlalchemy import event, text

from app_client import client_for
from core import association as association_setting
from core.idmapper.idmapper import catalog_oid_to_masterid
from core.repository.association_models import (
    ASSOCIATION_SCHEMA,
    AssociationBase,
    AssociationMethod,
    ObjectAssociation,
    ObjectGroup,
)
from object_api.services import counterpart_service

ZTF_GROUPED, ZTF_ALONE = "ZTF20aaaaaaa", "ZTF20aaaaaab"
LSST_X = 170441932397871511


@pytest.fixture
def objects(db, monkeypatch):
    """Two ZTF objects in the results; the first is in a group with an LSST object."""
    monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", ASSOCIATION_SCHEMA)
    with db.session() as session:
        session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {ASSOCIATION_SCHEMA}"))
        session.commit()
    AssociationBase.metadata.create_all(db._engine)

    grouped, alone = (catalog_oid_to_masterid("ZTF", name).item() for name in (ZTF_GROUPED, ZTF_ALONE))
    with db.session() as session:
        session.add_all(
            [
                Object(oid=oid, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010)
                for oid in (grouped, alone)
            ]
            + [Object(oid=LSST_X, tid=1, sid=1, meanra=10.0, meandec=10.0, firstmjd=61000, lastmjd=61010, n_det=12)]
        )
        session.commit()
        for oid in (grouped, alone):
            session.add(ZtfObject(oid=oid, stellar=False, corrected=False))
            session.add(
                Probability(
                    oid=oid,
                    sid=0,
                    classifier_id=2,
                    classifier_version=1,
                    class_id=3,
                    probability=0.5,
                    ranking=1,
                    lastmjd=60010,
                )
            )
        session.add_all(
            [
                AssociationMethod(method_version=3, method_name="test", params={"groups": {"threshold": 0.95}}),
                ObjectGroup(oid=grouped, sid=0, group_id=7, group_version=1, method_version=3),
                ObjectGroup(oid=LSST_X, sid=1, group_id=7, group_version=1, method_version=3),
                ObjectAssociation(
                    oid_a=grouped, sid_a=0, oid_b=LSST_X, sid_b=1, method_version=3, dist=0.4, score=0.99
                ),
            ]
        )
        session.commit()

    yield db

    AssociationBase.metadata.drop_all(db._engine)
    with db.session() as session:
        session.execute(text("DELETE FROM probability"))
        session.execute(text("DELETE FROM ztf_object"))
        session.commit()


def _rows(html: str) -> dict[str, str]:
    """Each result row's HTML, by the oid it shows."""
    rows = html.split('name="object_row_element"')[1:]
    return {row.split('<span name="oid">')[1].split("</span>")[0]: row for row in rows}


def test_a_grouped_object_links_to_its_counterpart(objects):
    response = client_for("object_api", objects).get("/htmx/list_objects", params={"survey": "ztf"})

    assert response.status_code == 200
    assert "Also seen as</th>" in response.text
    rows = _rows(response.text)
    assert "LSST ×1</summary>" in rows[ZTF_GROUPED]
    assert f'href="/object/{LSST_X}?survey=lsst"' in rows[ZTF_GROUPED]
    assert f'title="{LSST_X} · 0.40&#34;, score 0.99 · 12 detections"' in rows[ZTF_GROUPED]
    assert "<details" not in rows[ZTF_ALONE]


def test_no_column_without_association_schema(objects, monkeypatch):
    monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", None)

    response = client_for("object_api", objects).get("/htmx/list_objects", params={"survey": "ztf"})

    assert response.status_code == 200
    assert "Also seen as" not in response.text
    assert set(_rows(response.text)) == {ZTF_GROUPED, ZTF_ALONE}


def test_a_failed_lookup_still_shows_the_results(objects, monkeypatch):
    def broken(*args):
        raise RuntimeError("no such schema")

    monkeypatch.setattr(counterpart_service, "get_counterparts", broken)

    response = client_for("object_api", objects).get("/htmx/list_objects", params={"survey": "ztf"})

    assert response.status_code == 200
    rows = _rows(response.text)
    assert set(rows) == {ZTF_GROUPED, ZTF_ALONE}
    assert all("<details" not in row for row in rows.values())


def test_the_column_costs_one_statement(objects, monkeypatch):
    """Each query is a round trip to a distant database in production, so the column must stay one statement."""
    statements = []
    listener = lambda *args: statements.append(args[2])  # noqa: E731  (args[2] is the SQL)
    event.listen(objects._engine, "before_cursor_execute", listener)
    try:
        client = client_for("object_api", objects)
        client.get("/htmx/list_objects", params={"survey": "ztf"})
        with_column = len(statements)
        statements.clear()
        monkeypatch.setattr(association_setting, "ASSOCIATION_SCHEMA", None)
        client.get("/htmx/list_objects", params={"survey": "ztf"})
        without_column = len(statements)
    finally:
        event.remove(objects._engine, "before_cursor_execute", listener)

    assert with_column - without_column == 1
