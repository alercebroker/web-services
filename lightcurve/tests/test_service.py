import pytest
from core.exceptions import AtlasNonDetectionError, SurveyIdError
from core.models import Detection as DetectionModel
from core.models import NonDetection as NonDetectionModel
from core.service import (
    _get_detections_mongo,
    _get_detections_sql,
    _get_forced_photometry_mongo,
    _get_forced_photometry_sql,
    _get_non_detections_mongo,
    _get_non_detections_sql,
    get_detections,
    get_lightcurve,
    get_non_detections,
    get_period,
)

required_detection_fields = {
    "candid",
    "tid",
    "oid",
    "mjd",
    "fid",
    "ra",
    "dec",
    "mag",
    "e_mag",
    "isdiffpos",
    "corrected",
    "dubious",
    "has_stamp",
}

required_non_detection_fields = {
    "aid",
    "tid",
    "sid",
    "oid",
    "mjd",
    "fid",
    "diffmaglim",
}

required_forced_photometry_fields = {
    "candid",
    "tid",
    "oid",
    "mjd",
    "fid",
    "ra",
    "dec",
    "mag",
    "e_mag",
    "isdiffpos",
    "corrected",
    "dubious",
    "has_stamp",
}


def test_get_ztf_detections(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert type(result[0]) is DetectionModel
    assert len(result) == 1
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 0
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 1


def test_get_ztf_detections_multiple_oids_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_many_oid_per_aid,
):
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert type(result[0]) is DetectionModel
    assert len(result) == 3
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 0
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 3


def test_get_atlas_detections_1_oid_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_atlas_1_oid_per_aid,
):
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert type(result[0]) is DetectionModel
    assert len(result) == 1
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 0
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 1


def test_get_atlas_detections_many_oid_per_aid(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_atlas_many_oid_per_aid,
):
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert type(result[0]) is DetectionModel
    assert len(result) == 2
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 0
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
    )
    assert len(result) == 2


def test_get_multistream_detections_all_surveys(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_many_aid_ztf_and_atlas_detections,
):
    # oid1 and oid3 are the same object multistream
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="all",
    )
    assert type(result[0]) is DetectionModel
    assert len(result) == 2
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="all",
    )
    assert len(result) == 2


def test_get_multistream_detections_ztf_survey(
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
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="ztf",
    )
    assert len(result) == 1
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="ztf",
    )
    assert len(result) == 1


def test_get_multistream_detections_atlas_survey(
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
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid1",
        survey_id="atlas",
    )
    assert len(result) == 1
    result = get_detections(
        session_factory=psql_session,
        mongo_db=mongo_database,
        oid="oid3",
        survey_id="atlas",
    )
    assert len(result) == 1


def test_get_detections_from_unknown_survey(
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
        get_detections(
            session_factory=psql_session,
            mongo_db=mongo_database,
            oid="oid1",
            survey_id="unknown",
        )


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


def test_get_ztf_lightcurve(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 1
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 0
    assert len(result["non_detections"]) == 0
    result = get_lightcurve(
        oid="oid1",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 1


def test_get_atlas_lightcurve(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    psql_session,
    init_psql,
    insert_atlas_1_oid_per_aid,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        mongo_db=mongo_database,
        session_factory=psql_session,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        mongo_db=mongo_database,
        session_factory=psql_session,
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 0
    assert len(result["non_detections"]) == 0
    result = get_lightcurve(
        oid="oid1", mongo_db=mongo_database, session_factory=psql_session
    )
    assert isinstance(result, dict)
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0


def test_get_multistream_lightcurve_ztf_survey(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    psql_session,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 2
    result = get_lightcurve(
        oid="oid3",
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 2


def test_get_multistream_lightcurve_atlas_survey(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    psql_session,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="atlas",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0
    result = get_lightcurve(
        oid="oid3",
        survey_id="atlas",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 1
    assert len(result["non_detections"]) == 0


def test_get_multistream_lightcurve_all_survey(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    psql_session,
    init_psql,
    insert_many_aid_ztf_and_atlas_detections,
):
    result = get_lightcurve(
        oid="oid1",
        survey_id="all",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 2
    result = get_lightcurve(
        oid="oid3",
        survey_id="all",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )
    assert len(result["detections"]) == 2
    assert len(result["non_detections"]) == 2


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


def test_get_mongo_detections(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_detections_mongo(
        database=mongo_database,
        oid="oid1",
        tid="ztf",
    )
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_mongo_detections_multiple_oids(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    insert_ztf_many_oid_per_aid,
):
    result = _get_detections_mongo(
        database=mongo_database,
        oid="oid1",
        tid="ztf",
    )
    assert len(result) == 3
    assert required_detection_fields.issubset(set(dict(result[0]).keys()))


def test_get_mongo_non_detections(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_non_detections_mongo(
        database=mongo_database,
        oid="oid1",
        tid="ztf",
    )
    assert required_non_detection_fields.issubset(set(dict(result[0]).keys()))


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


def test_get_mongo_forced_photometry(
    mongo_service,
    mongo_database,
    init_mongo,
    psql_service,
    init_psql,
    insert_ztf_1_oid_per_aid,
):
    result = _get_forced_photometry_mongo(
        mongo_database,
        oid="oid1",
        tid="ztf",
    )
    assert required_forced_photometry_fields.issubset(
        set(dict(result[0]).keys())
    )


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


def test_get_period(
    psql_service,
    psql_session,
    init_psql,
    mongo_service,
    mongo_database,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_period(
        oid="oid1",
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
    )

    assert abs(result.value - 296.87498481917) < 0.00001
