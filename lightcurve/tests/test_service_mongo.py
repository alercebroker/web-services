from core.services.lightcurve_service import (
    _get_detections_mongo,
    _get_forced_photometry_mongo,
    _get_non_detections_mongo,
)

from test_utils import (
    required_detection_fields,
    required_forced_photometry_fields,
    required_non_detection_fields,
)


def test_get_mongo_detections(
    init_mongo,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_detections_mongo(
        database=init_mongo,
        oid="oid1",
        tid="ztf",
    )
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_mongo_detections_multiple_oids(
    init_mongo,
    init_psql,
    insert_ztf_many_oid_per_aid,
):
    result = _get_detections_mongo(
        database=init_mongo,
        oid="oid1",
        tid="ztf",
    )
    assert len(result) == 3
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_mongo_non_detections(
    init_mongo,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_non_detections_mongo(
        database=init_mongo,
        oid="oid1",
        tid="ztf",
    )
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_mongo_forced_photometry(
    init_mongo,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_forced_photometry_mongo(
        init_mongo,
        oid="oid1",
        tid="ztf",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 1


def test_get_mongo_forced_photometry_multiple_oids(
    init_mongo,
    init_psql,
    insert_ztf_many_oid_per_aid,
):
    result = _get_forced_photometry_mongo(
        init_mongo,
        oid="oid1",
        tid="ztf",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 3


def test_get_mongo_forced_photometry_multistream(
    init_mongo,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = _get_forced_photometry_mongo(
        init_mongo,
        oid="oid1",
        tid="all",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )
    assert len(result) == 2
