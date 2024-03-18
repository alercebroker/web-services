from core.service import get_period


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
