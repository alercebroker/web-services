"""The "Also seen as" column of the results table, without a database: the repository is faked."""

from types import SimpleNamespace

import pytest

from core.idmapper.idmapper import catalog_oid_to_masterid
from object_api.routes import htmx
from object_api.services import counterpart_service

ZTF_A, ZTF_B, ZTF_ALONE = "ZTF20aaaaaaa", "ZTF20aaaaaab", "ZTF20aaaaaac"
A, B, ALONE = (catalog_oid_to_masterid("ZTF", name).item() for name in (ZTF_A, ZTF_B, ZTF_ALONE))
LSST_X, LSST_Y = 170441932397871511, 170441932397871512
SESSION = None  # the repository is faked: no queries reach it


def fake_rows(members: list[tuple[int, int]], pairs: dict, n_det: dict):
    """A get_counterpart_rows for one group: each listed member gets a row per other member, with their direct
    pair's dist and score (None without one) and the other member's n_det (None when unknown)."""

    def get_counterpart_rows(session_factory, objects):
        rows = []
        for listed in objects:
            if listed not in members:
                continue
            for other in members:
                if other == listed:
                    continue
                dist, score = pairs.get(frozenset([listed, other]), (None, None))
                rows.append(
                    SimpleNamespace(
                        listed_oid=listed[0],
                        listed_sid=listed[1],
                        oid=other[0],
                        sid=other[1],
                        dist=dist,
                        score=score,
                        n_det=n_det.get(other),
                    )
                )
        return rows

    return get_counterpart_rows


@pytest.fixture
def repository(monkeypatch):
    """ZTF_A is in a group with LSST_X (paired with it), LSST_Y (joined through LSST_X) and ZTF_B, a duplicate.

    ZTF_ALONE has no group.
    """
    members = [(A, 0), (LSST_X, 1), (LSST_Y, 1), (B, 0)]
    pairs = {frozenset([(A, 0), (LSST_X, 1)]): (0.4, 0.99), frozenset([(A, 0), (B, 0)]): (1.1, 0.97)}
    n_det = {(LSST_X, 1): 12, (LSST_Y, 1): 40}
    monkeypatch.setattr(
        counterpart_service.association_repository, "get_counterpart_rows", fake_rows(members, pairs, n_det)
    )


def test_members_are_grouped_by_survey_other_surveys_first(repository):
    found = counterpart_service.get_counterparts(SESSION, "ztf", [ZTF_A, ZTF_ALONE])

    assert list(found) == [ZTF_A]  # an object without a group gets no entry
    lsst, ztf = found[ZTF_A]
    assert (lsst.label, lsst.count, ztf.label, ztf.count) == ("LSST", 2, "ZTF", 1)
    # The directly paired member comes first, then the one that joined through it
    assert [m.oid for m in lsst.members] == [str(LSST_X), str(LSST_Y)]
    assert lsst.members[0].description == f'{LSST_X} · 0.40", score 0.99 · 12 detections'
    assert lsst.members[1].description == f"{LSST_Y} · linked through another member · 40 detections"
    assert ztf.members[0].oid == ZTF_B
    assert ztf.members[0].description == f'{ZTF_B} · 1.10", score 0.97'  # not in the object table: no detections


def test_the_chip_lists_at_most_ten_members_but_counts_them_all(monkeypatch):
    members = [(A, 0), *((LSST_X + i, 1) for i in range(15))]
    monkeypatch.setattr(counterpart_service.association_repository, "get_counterpart_rows", fake_rows(members, {}, {}))

    (lsst,) = counterpart_service.get_counterparts(SESSION, "ztf", [ZTF_A])[ZTF_A]

    assert (lsst.count, len(lsst.members)) == (15, counterpart_service.MAX_LISTED_PER_SURVEY)
    assert lsst.title.endswith("… and 5 more")


def test_an_lsst_listing_is_keyed_by_the_numeric_id(repository):
    found = counterpart_service.get_counterparts(SESSION, "lsst", [str(LSST_X)])

    assert [(s.label, [m.oid for m in s.members]) for s in found[str(LSST_X)]] == [
        ("ZTF", [ZTF_A, ZTF_B]),
        ("LSST", [str(LSST_Y)]),
    ]


def test_the_column_is_off_without_association_schema(monkeypatch):
    monkeypatch.delenv("ASSOCIATION_SCHEMA", raising=False)

    assert htmx._counterparts(None, "ztf", [ZTF_A]) is None


def test_a_failed_lookup_leaves_the_column_empty(monkeypatch):
    monkeypatch.setenv("ASSOCIATION_SCHEMA", "association")

    def broken(*args):
        raise RuntimeError("no such schema")

    monkeypatch.setattr(counterpart_service, "get_counterparts", broken)

    assert htmx._counterparts(None, "ztf", [ZTF_A]) == {}
