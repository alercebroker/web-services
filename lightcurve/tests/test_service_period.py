from core.services.lightcurve_service import get_period


def test_get_period(
    init_psql,
    init_mongo,
    insert_ztf_1_oid_per_aid,
):
    result = get_period(
        oid="oid1",
        survey_id="ztf",
        session_factory=init_psql.session,
    )
    assert result
    assert result.value is not None
    assert abs(result.value - 296.87498481917) < 0.00001
