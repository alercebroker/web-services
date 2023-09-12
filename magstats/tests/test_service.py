from core.service import get_magstats
from core.exceptions import SurveyIdError
import pytest


def test_get_ztf_magstats(psql_service, psql_session, init_psql):
    result = get_magstats(
        session_factory=psql_session,
        oid="oid1",
        survey_id="ztf",
    )
    assert result[0].fid == 123 

def test_get_magstats_from_unknown_survey(
    psql_service, psql_session, init_psql
):
    with pytest.raises(
        SurveyIdError, match="Can't retrieve magstats survey id not recognized unknown"
    ):
        get_magstats(
            session_factory=psql_session,
            oid="oid1",
            survey_id="unknown",
        )


def test_get_atlas_magstats(mongo_service, mongo_database, init_mongo):
    result = get_magstats(
        oid="oid1",
        survey_id="atlas",
        mongo_db=mongo_database,
    )
    assert result[0]["tid"] == "atlas" 

