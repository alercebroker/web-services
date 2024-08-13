import pytest
from core.exceptions import SurveyIdError
from core.model import Detection as DetectionModel
from core.service import get_detections


def test_get_ztf_detections(
    init_psql,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result
    assert type(result[0]) is DetectionModel
    assert len(result) == 1
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="atlas",
    )
    assert result is not None
    assert len(result) == 0
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result
    assert len(result) == 1


def test_get_ztf_detections_multiple_oids_per_aid(
    init_psql,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result
    assert type(result[0]) is DetectionModel
    assert len(result) == 3
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="atlas",
    )
    assert result is not None
    assert len(result) == 0
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result
    assert len(result) == 3


def test_get_atlas_detections_1_oid_per_aid(
    init_psql,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="atlas",
    )
    assert result
    assert type(result[0]) is DetectionModel
    assert len(result) == 1
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result is not None
    assert len(result) == 0
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result
    assert len(result) == 1


def test_get_atlas_detections_many_oid_per_aid(
    init_psql,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="atlas",
    )
    assert result is not None
    assert type(result[0]) is DetectionModel
    assert len(result) == 2
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result is not None
    assert len(result) == 0
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
    )
    assert result is not None
    assert len(result) == 2


def test_get_multistream_detections_all_surveys(
    init_psql,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same object multistream
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="all",
    )
    assert result is not None
    assert type(result[0]) is DetectionModel
    assert len(result) == 2
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid3",
        survey_id="all",
    )
    assert result is not None
    assert len(result) == 2


def test_get_multistream_detections_ztf_survey(
    init_psql,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same multistream object
    # but oid3 is not on ztf
    # so asking for oid3 on survey ztf should return detections from oid1
    # and these detections should be found on mongo database
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="ztf",
    )
    assert result is not None
    assert len(result) == 1
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid3",
        survey_id="ztf",
    )
    assert result is not None
    assert len(result) == 1


def test_get_multistream_detections_atlas_survey(
    init_psql,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same object aid1
    # but oid1 is not on atlas
    # so asking for oid1 on survey atlas should return detections from oid3
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid1",
        survey_id="atlas",
    )
    assert result is not None
    assert len(result) == 1
    result = get_detections(
        session_factory=init_psql.session,
        mongo_db=init_mongo,
        oid="oid3",
        survey_id="atlas",
    )
    assert result is not None
    assert len(result) == 1


def test_get_detections_from_unknown_survey(
    init_psql,
    init_mongo,
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_detections(
            session_factory=init_psql.session,
            mongo_db=init_mongo,
            oid="oid1",
            survey_id="unknown",
        )
