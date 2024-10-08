import os

from test_utils import create_token
from core.services.lightcurve_service import remove_duplicate_forced_photometry_by_pid


def test_forced_photometry_from_ztf(
    test_client,
    insert_ztf_1_oid_per_aid,
):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "ztf"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_forced_photometry_from_atlas_unauthenticated(
    test_client,
    insert_atlas_1_oid_per_aid,
):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "atlas"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_forced_photometry_from_atlas_forbidden(
    test_client,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(["forbidden"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get(
        "/forced-photometry/oid1",
        params={"survey_id": "atlas"},
        headers=headers,
    )
    assert res.status_code == 403


def test_forced_photometry_from_atlas_authenticated_without_filters(
    test_client,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(["basic_user"], [""], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get(
        "/forced-photometry/oid1",
        params={"survey_id": "atlas"},
        headers=headers,
    )
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_forced_photometry_from_atlas_authenticated_with_filters(
    test_client,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(
        ["basic_user"],
        ["filter_atlas_forced_photometry"],
        os.getenv("SECRET_KEY"),
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get(
        "/forced-photometry/oid1",
        params={"survey_id": "atlas"},
        headers=headers,
    )
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_forced_photometry_multistream_unauthenticated(
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    res = test_client.get("/forced-photometry/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_forced_photometry_multistream_authenticated_without_filter(
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"],
        [],
        os.getenv("SECRET_KEY"),
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/forced-photometry/oid1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_forced_photometry_multistream_authenticated_with_filter(
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"],
        ["filter_atlas_forced_photometry"],
        os.getenv("SECRET_KEY"),
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/forced-photometry/oid1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_forced_photometry_with_duplicate_pids():
    detections = [{"pid": 1}, {"pid": 2}, {"pid": 3}]
    forced_photometry = [{"pid": 1}, {"pid": 1}, {"pid": 2}, {"pid": 4}]
    result = remove_duplicate_forced_photometry_by_pid(detections, forced_photometry)
    assert len(result) == 1
    assert result[0]["pid"] == 4
    detections = []
    forced_photometry = [{"pid": 1}, {"pid": 1}, {"pid": 2}, {"pid": 4}]
    result = remove_duplicate_forced_photometry_by_pid(detections, forced_photometry)
    assert len(result) == 3
    assert result[0]["pid"] == 1
    assert result[1]["pid"] == 2
    assert result[2]["pid"] == 4
    detections = [{"pid": 1}, {"pid": 2}, {"pid": 3}]
    forced_photometry = []
    result = remove_duplicate_forced_photometry_by_pid(detections, forced_photometry)
    assert len(result) == 0
