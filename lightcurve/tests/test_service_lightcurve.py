import pytest
from core.exceptions import SurveyIdError
from core.service import get_lightcurve


def test_get_ztf_lightcurve(
    init_psql,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 1
    assert len(result["forced_photometry"]) == 1
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 0
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 0
    result = get_lightcurve(
        oid="oid1",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 1
    assert len(result["forced_photometry"]) == 1


def test_get_atlas_lightcurve(
    init_mongo,
    init_psql,
    insert_atlas_1_oid_per_aid,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        mongo_db=init_mongo,
        session_factory=init_psql.session,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 1
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        mongo_db=init_mongo,
        session_factory=init_psql.session,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 0
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 0
    result = get_lightcurve(
        oid="oid1", mongo_db=init_mongo, session_factory=init_psql.session
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 1


def test_get_multistream_lightcurve_ztf_survey(
    init_mongo,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 2
    assert len(result["forced_photometry"]) == 1
    result = get_lightcurve(
        oid="oid3",
        survey_id="ztf",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 2
    assert len(result["forced_photometry"]) == 1


def test_get_multistream_lightcurve_atlas_survey(
    init_mongo,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 1
    result = get_lightcurve(
        oid="oid3",
        survey_id="atlas",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    assert len(result["forced_photometry"]) == 1


def test_get_multistream_lightcurve_all_survey(
    init_mongo,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="all",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 2
    assert len(result["forced_photometry"]) == 2
    result = get_lightcurve(
        oid="oid3",
        survey_id="all",
        session_factory=init_psql.session,
        mongo_db=init_mongo,
    )
    assert result is not None
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 2
    assert len(result["forced_photometry"]) == 2


def test_get_lightcurve_from_unknown_survey(
    init_mongo,
    init_psql,
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_lightcurve(
            oid="oid1",
            survey_id="unknown",
            session_factory=init_psql.session,
            mongo_db=init_mongo,
        )
