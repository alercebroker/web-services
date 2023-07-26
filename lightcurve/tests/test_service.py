from core.service import get_detections, get_non_detections
import pytest


def test_get_ztf_detections(psql_service, psql_database):
    result = get_detections(
        session_factory=psql_database.session, oid="oid1", survey_id="ztf"
    )
    assert len(result) == 2


def test_get_detections_from_unknown_survey(psql_service, psql_database):
    with pytest.raises(Exception, match="survey id not recognized unknown"):
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
    with pytest.raises(Exception, match="survey id not recognized unknown"):
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
        Exception,
        match="Can't retrieve non detections: ATLAS does not provide non_detections",
    ):
        get_non_detections(
            oid="oid1",
            survey_id="atlas",
            mongo_db=mongo_database,
        )
