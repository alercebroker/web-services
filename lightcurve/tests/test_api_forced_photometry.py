import os

from test_utils import create_token


def test_forced_photometry_from_ztf(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "ztf"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_forced_photometry_from_atlas_unauthenticated(
    mongo_service,
    init_mongo,
    test_client,
    psql_service,
    init_psql,
    psql_session,
    insert_atlas_1_oid_per_aid,
):
    res = test_client.get(
        "/forced-photometry/oid1", params={"survey_id": "atlas"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_forced_photometry_from_atlas_forbidden(
    mongo_service,
    init_mongo,
    test_client,
    psql_service,
    init_psql,
    psql_session,
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
    mongo_service,
    init_mongo,
    test_client,
    psql_service,
    init_psql,
    psql_session,
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
    assert len(res.json()) == 1


def test_forced_photometry_from_atlas_authenticated_with_filters(
    mongo_service,
    init_mongo,
    test_client,
    psql_service,
    init_psql,
    psql_session,
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
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    res = test_client.get("/forced-photometry/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_forced_photometry_multistream_authenticated_without_filter(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
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
    assert len(res.json()) == 2


def test_forced_photometry_multistream_authenticated_with_filter(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
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
