from core.service import get_detections, get_non_detections, get_lightcurve
from core.exceptions import SurveyIdError, AtlasNonDetectionError
from core.models import (
    Detection as DetectionModel,
    NonDetection as NonDetectionModel,
)
import pytest


def test_get_ztf_detections(
    psql_service, psql_session, init_psql,
    mongo_service, mongo_database, init_mongo
):
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 3
    assert type(result[0]) is DetectionModel


def test_get_detections_from_unknown_survey(
    psql_service, psql_session, init_psql,
    mongo_service, mongo_database, init_mongo
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_detections(
            session_factory=psql_session,
        mongo_db=mongo_database,
            oid="oid1",
            survey_id="unknown",
        )


def test_get_ztf_non_detections(
    psql_service, psql_session, init_psql,
    mongo_service, mongo_database, init_mongo
):
    result = get_non_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf"
    )
    assert len(result) == 3
    assert type(result[0]) is NonDetectionModel


def test_get_non_detections_from_unknown_survey(
    psql_service, psql_session, init_psql,
    mongo_service, mongo_database, init_mongo
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


def test_get_atlas_detections(mongo_service, mongo_database, init_mongo):
    result = get_detections(
        oid="oid2",
        survey_id="atlas",
        mongo_db=mongo_database,
    )
    assert len(result) == 2
    assert type(result[0]) is DetectionModel


def test_get_atlas_non_detections(mongo_service, mongo_database, init_mongo):
    with pytest.raises(
        AtlasNonDetectionError,
        match="Can't retrieve non detections: ATLAS does not provide non_detections",
    ):
        get_non_detections(
            oid="oid2",
            survey_id="atlas",
            mongo_db=mongo_database,
        )


def test_get_ztf_lightcurve(
    psql_service, psql_session, init_psql,
    mongo_service, mongo_database, init_mongo
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 3
    assert len(result["non_detections"]) == 3


def test_get_atlas_lightcurve(mongo_service, mongo_database, init_mongo):
    result = get_lightcurve(
        oid="oid2", survey_id="atlas", mongo_db=mongo_database
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 0


def test_get_lightcurve_from_unknown_survey(
    psql_service,
    psql_session,
    mongo_service,
    mongo_database,
    init_psql,
    init_mongo,
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_lightcurve(
            oid="oid1",
            survey_id="unknown",
            session_factory=psql_session,
            mongo_db=mongo_database,
        )
