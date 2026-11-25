"""The group panel's logic, without a database: who is a member, how each is described, who is nearby."""

from types import SimpleNamespace

import pytest

from core.idmapper import idmapper
from lightcurve_api.services.group_service import build_group_info, display_oid, parse_object_keys

ZTF_A = idmapper.catalog_oid_to_masterid("ZTF", "ZTF18abvkqpo").item()
ZTF_B = idmapper.catalog_oid_to_masterid("ZTF", "ZTF19aaxlmra").item()
ZTF_C = idmapper.catalog_oid_to_masterid("ZTF", "ZTF20acwxyzq").item()
LSST_X = 313853798223069211
LSST_SS = 99  # an LSST solar-system object (sid 2): never shown


def pair(a, b, dist, score):
    (oid_a, sid_a), (oid_b, sid_b) = sorted([a, b], key=lambda k: (k[1], k[0]))
    return SimpleNamespace(oid_a=oid_a, sid_a=sid_a, oid_b=oid_b, sid_b=sid_b, dist=dist, score=score)


def build(self_key, members, pairs, **kwargs):
    return build_group_info(self_key, members, pairs, threshold=0.95, method_version=3, **kwargs)


def test_viewed_object_comes_first_and_members_by_score():
    a, b, x = (ZTF_A, 0), (ZTF_B, 0), (LSST_X, 1)
    info = build(x, [a, b, x], [pair(x, a, 0.25, 0.98), pair(x, b, 0.69, 0.97)], group_id=48213, group_version=3)

    assert [m.oid for m in info.members] == [str(LSST_X), "ZTF18abvkqpo", "ZTF19aaxlmra"]
    assert info.members[0].is_self and info.members[0].score is None
    assert (info.members[1].dist, info.members[1].score) == (0.25, 0.98)
    assert (info.group_id, info.group_version) == (48213, 3)


def test_member_without_a_direct_pair_is_described_through_another_member():
    a, b, x = (ZTF_A, 0), (ZTF_B, 0), (LSST_X, 1)
    info = build(x, [a, b, x], [pair(x, a, 0.25, 0.98), pair(a, b, 0.4, 0.99)])

    via = next(m for m in info.members if m.oid == "ZTF19aaxlmra")
    assert (via.score, via.linked_via) == (0.99, "ZTF18abvkqpo")
    assert info.members[-1] is via  # direct pairs first


def test_nearby_objects_are_non_members_strongest_pair_first():
    a, x, c = (ZTF_A, 0), (LSST_X, 1), (ZTF_C, 0)
    pairs = [pair(x, a, 0.25, 0.98), pair(x, c, 2.1, 0.01), pair(a, c, 2.3, 0.3), pair(a, (LSST_SS, 2), 1.0, 0.5)]
    info = build(x, [a, x], pairs)

    assert [n.oid for n in info.nearby] == ["ZTF20acwxyzq"]  # once, and never the solar-system object
    assert (info.nearby[0].score, info.nearby[0].linked_via) == (0.3, "ZTF18abvkqpo")
    assert not info.nearby[0].in_group


def test_ungrouped_object_has_only_itself_and_its_neighbours():
    x, c = (LSST_X, 1), (ZTF_C, 0)
    info = build(x, [x], [pair(x, c, 2.1, 0.01)])

    assert len(info.members) == 1 and info.group_id is None
    assert [n.oid for n in info.nearby] == ["ZTF20acwxyzq"]
    assert info.nearby[0].linked_via is None  # paired with the viewed object itself


def test_nearby_list_is_capped():
    x = (LSST_X, 1)
    neighbours = [(1000 + i, 1) for i in range(8)]
    info = build(x, [x], [pair(x, n, 1.0 + i, 0.1 * i) for i, n in enumerate(neighbours)], nearby_limit=3)

    assert [n.oid for n in info.nearby] == ["1007", "1006", "1005"]


def test_keys_and_json_ids_are_strings():
    info = build((LSST_X, 1), [(LSST_X, 1)], [])
    member = info.to_dict()["members"][0]

    assert member["oid"] == str(LSST_X) and member["key"] == f"lsst:{LSST_X}"


def test_display_oid():
    assert display_oid(ZTF_A, 0) == "ZTF18abvkqpo"
    assert display_oid(LSST_X, 1) == str(LSST_X)


def test_parse_object_keys_groups_by_survey():
    assert parse_object_keys(f"ztf:ZTF18abvkqpo, LSST:{LSST_X},ztf:{ZTF_B}") == {
        "ztf": ["ZTF18abvkqpo", str(ZTF_B)],
        "lsst": [str(LSST_X)],
    }
    assert parse_object_keys("") == {}


@pytest.mark.parametrize(
    "objects",
    ["ZTF18abvkqpo", "atlas:1", "ztf:notaname", "lsst:ZTF18abvkqpo", ",".join(f"lsst:{i}" for i in range(21))],
)
def test_parse_object_keys_rejects(objects):
    with pytest.raises(ValueError):
        parse_object_keys(objects)
