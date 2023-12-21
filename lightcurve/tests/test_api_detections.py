from test_utils import create_token
import os


def test_ztf_detections(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    res = test_client.get("/detections/oid1?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid1?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_ztf_detections_multiple_oids_per_aid(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    res = test_client.get("/detections/oid1?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 3
    res = test_client.get("/detections/oid1?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_get_atlas_detections_1_oid_per_aid_unauthenticated(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    # unauthenticated requests filter all atlas
    res = test_client.get("/detections/oid1?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_atlas_detections_1_oid_per_aid_forbidden(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(["useles_permission"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 403


def test_get_atlas_detections_1_oid_per_aid_authenticated_no_filter(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_atlas_detections_1_oid_per_aid_authenticated_with_filter(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_atlas_detections_many_oid_per_aid_unauthenticated(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    # unauthenticated requests filter all atlas
    res = test_client.get("/detections/oid1?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_atlas_detections_many_oid_per_aid_forbidden(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    token = create_token(["forbidden"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/detections/oid1", headers=headers)
    assert res.status_code == 403


def test_get_atlas_detections_many_oid_per_aid_authenticated_without_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_atlas_detections_many_oid_per_aid_authenticated_with_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_multistream_detections_all_surveys_unauthenticated(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # unauthenticated requests filter all atlas
    res = test_client.get("/detections/oid1?survey_id=all")
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=all")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_all_surveys_forbidden(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["forbidden"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=all", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/detections/oid3?survey_id=all", headers=headers)
    assert res.status_code == 403


def test_get_multistream_detections_all_surveys_authenticated_without_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    res = test_client.get("/detections/oid3?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_multistream_detections_all_surveys_authenticated_with_filters(
    psql_service,
    init_psql,
    test_client,
    mongo_service,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=all", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_ztf_survey_unauthenticated(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    res = test_client.get("/detections/oid1?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=ztf")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_ztf_survey_forbidden(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["forbidden"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/detections/oid3?survey_id=ztf", headers=headers)
    assert res.status_code == 403


def test_get_multistream_detections_ztf_survey_authenticated_without_filters(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_ztf_survey_authenticated_with_filters(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=ztf", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_atlas_survey_unauthenticated(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    res = test_client.get("/detections/oid1?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid3?survey_id=atlas")
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_multistream_detections_atlas_survey_forbidden(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["forbidden"], [""], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 403
    res = test_client.get("/detections/oid3?survey_id=atlas", headers=headers)
    assert res.status_code == 403


def test_get_multistream_detections_atlas_survey_authenticated_without_filters(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(["basic_user"], [], os.getenv("SECRET_KEY"))
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get("/detections/oid3?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_multistream_detections_atlas_survey_authenticated_with_filters(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    token = create_token(
        ["basic_user"], ["filter_atlas_detections"], os.getenv("SECRET_KEY")
    )
    headers = {"Authorization": "bearer " + token}
    res = test_client.get("/detections/oid1?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = test_client.get("/detections/oid3?survey_id=atlas", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_get_detections_from_unknown_survey(
    psql_service,
    init_psql,
    mongo_service,
    init_mongo,
    test_client,
):
    res = test_client.get("/detections/oid1?survey_id=unknown")
    assert res.status_code == 400
