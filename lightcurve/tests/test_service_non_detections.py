import pytest
from core.exceptions import AtlasNonDetectionError, SurveyIdError
from core.models import NonDetection as NonDetectionModel
from core.service import get_non_detections
from utils import required_non_detection_fields


def test_get_ztf_non_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_non_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert type(result[0]) is NonDetectionModel
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))
    assert len(result) == 1
    result = get_non_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 1


def test_get_atlas_non_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    with pytest.raises(
        AtlasNonDetectionError,
        match="Can't retrieve non detections: ATLAS does not provide non_detections",
    ):
        get_non_detections(
            session_factory=psql_session,
            mongo_db=mongo_database,
            oid="oid1",
            survey_id="atlas",
        )


def test_get_multistream_non_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_non_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 2


def test_get_non_detections_from_unknown_survey(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_non_detections(
            session_factory=psql_session,
            mongo_db=mongo_database,
            oid="oid1",
            survey_id="unknown",
        )
