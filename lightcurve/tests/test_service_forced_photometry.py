import pytest
from core.exceptions import SurveyIdError
from core.models import ForcedPhotometry as ForcedPhotometryModel
from core.service import get_forced_photometry


def test_get_ztf_forced_photometry(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert type(result[0]) is ForcedPhotometryModel
    assert len(result) == 1
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 0
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 1


def test_get_ztf_forced_photometry_multiple_oids_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert type(result[0]) is ForcedPhotometryModel
    assert len(result) == 3
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 0
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 3


def test_get_atlas_forced_photometry_1_oid_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert type(result[0]) is ForcedPhotometryModel
    assert len(result) == 1
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 0
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 1


def test_get_atlas_forced_photometry_many_oid_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert type(result[0]) is ForcedPhotometryModel
    assert len(result) == 2
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 0
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 2


def test_get_multistream_forced_photometry_all_surveys(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same object multistream
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="all",
    )
    assert type(result[0]) is ForcedPhotometryModel
    assert len(result) == 2
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="all",
    )
    assert len(result) == 2


def test_get_multistream_forced_photometry_ztf_survey(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same multistream object
    # but oid3 is not on ztf
    # so asking for oid3 on survey ztf should return detections from oid1
    # and these detections should be found on mongo database
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 1
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="ztf",
    )
    assert len(result) == 1


def test_get_multistream_forced_photometry_atlas_survey(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same object aid1
    # but oid1 is not on atlas
    # so asking for oid1 on survey atlas should return detections from oid3
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 1
    result = get_forced_photometry(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="atlas",
    )
    assert len(result) == 1


def test_get_forced_photometry_from_unknown_survey(
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
        get_forced_photometry(
            session_factory=psql_session,
            mongo_db=mongo_database,
            oid="oid1",
            survey_id="unknown",
        )
