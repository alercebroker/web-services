from core.service import get_detections, get_non_detections, get_lightcurve
from core.exceptions import SurveyIdError, AtlasNonDetectionError
import pytest


def test_get_ztf_detections(psql_service, psql_database):
    result = get_detections(
        session_factory=psql_database.session,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 2


def test_get_detections_from_unknown_survey(psql_service, psql_database):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_detections(
            session_factory=psql_database.session,
            oid="oid1",
            survey_id="unknown",
        )


def test_get_ztf_non_detections(psql_service, psql_database):
    result = get_non_detections(
        session_factory=psql_database.session, oid="oid1", survey_id="ztf"
    )
    assert len(result) == 2


def test_get_non_detections_from_unknown_survey(psql_service, psql_database):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_non_detections(
            session_factory=psql_database.session,
            oid="oid1",
            survey_id="unknown",
        )


def test_get_atlas_detections(mongo_service, mongo_database):
    result = get_detections(
        oid="oid1",
        survey_id="atlas",
        mongo_db=mongo_database,
    )
    assert len(result) == 2


def test_get_atlas_non_detections(mongo_service, mongo_database):
    with pytest.raises(
        AtlasNonDetectionError,
        match="Can't retrieve non detections: ATLAS does not provide non_detections",
    ):
        get_non_detections(
            oid="oid1",
            survey_id="atlas",
            mongo_db=mongo_database,
        )


def test_get_ztf_lightcurve(psql_service, psql_database):
    result = get_lightcurve(
        oid="oid1", survey_id="ztf", session_factory=psql_database.session
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 2


def test_get_atlas_lightcurve(mongo_service, mongo_database):
    result = get_lightcurve(
        oid="oid1", survey_id="atlas", mongo_db=mongo_database
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 0


def test_get_lightcurve_from_unknown_survey(
    psql_service, psql_database, mongo_service, mongo_database
):
    with pytest.raises(
        SurveyIdError, match="survey id not recognized unknown"
    ):
        get_lightcurve(
            oid="oid1",
            survey_id="unknown",
            session_factory=psql_database.session,
            mongo_db=mongo_database,
        )
