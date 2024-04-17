import pytest
from core.exceptions import AtlasNonDetectionError, SurveyIdError
from core.models import NonDetection as NonDetectionModel
from core.service import get_non_detections
from test_utils import required_non_detection_fields


def test_get_ztf_non_detections(
    init_psql,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_non_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result is not None
    assert type(result[0]) is NonDetectionModel
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))
    assert len(result) == 1
    result = get_non_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result is not None
    assert len(result) == 1


def test_get_ztf_non_detections_with_many_oid_per_aid(
    init_psql,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    result = get_non_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result is not None
    assert type(result[0]) is NonDetectionModel
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))
    assert len(result) == 3
    result = get_non_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result is not None
    assert len(result) == 3


def test_get_atlas_non_detections(
    init_psql,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    with pytest.raises(
        AtlasNonDetectionError,
        match="Can't retrieve non detections: ATLAS does not provide non_detections",
    ):
        get_non_detections(
            session_factory=init_psql.session,
            mongo_db=init_mongo,
            oid="oid1",
            survey_id="atlas",
        )


def test_get_multistream_non_detections(
    init_psql,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_non_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result is not None
    assert len(result) == 2


def test_get_non_detections_from_unknown_survey(
    init_psql,
    init_mongo,
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_non_detections(
            session_factory=init_psql.session,
            mongo_db=init_mongo,
            oid="oid1",
            survey_id="unknown",
        )
