from core.service import (
    _get_detections_sql,
    _get_forced_photometry_sql,
    _get_non_detections_sql,
)

from test_utils import (
    required_detection_fields,
    required_forced_photometry_fields,
    required_non_detection_fields,
)


def test_get_sql_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = _get_detections_sql(
        session_factory=psql_session,
        oid="oid1",
        tid="ztf",
    )
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_sql_detections_multiple_oids(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    result = _get_detections_sql(
        session_factory=psql_session,
        oid="oid1",
        tid="ztf",
    )
    assert len(result) == 1
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_sql_non_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = _get_non_detections_sql(
        session_factory=psql_session,
        oid="oid1",
        tid="ztf",
    )
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_sql_forced_photometry(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = _get_forced_photometry_sql(
        psql_session,
        oid="oid1",
        tid="ztf",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 1


def test_get_sql_forced_photometry_multiple_oids(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    psql_session,
    insert_ztf_many_oid_per_aid,
):
    result = _get_forced_photometry_sql(
        psql_session,
        oid="oid1",
        tid="ztf",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 1


def test_get_sql_forced_photometry_multistream(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    psql_session,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = _get_forced_photometry_sql(
        psql_session,
        oid="oid1",
        tid="all",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 1
