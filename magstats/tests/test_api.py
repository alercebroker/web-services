def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


def test_magstats_without_survey_id_param(
    psql_service, init_psql, test_client
):
    res = test_client.get("/magstats/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 1 #esto puede cambiar en el contexto de magstats


def test_magstats_from_ztf(psql_service, init_psql, test_client):
    res = test_client.get("/magstats/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 1 #esto puede cambiar en el contexto de magstats




def test_magstats_from_atlas(mongo_service, init_mongo, test_client):
    res = test_client.get("/magstats/oid1", params={"survey_id": "atlas"})
    assert res.status_code == 200
    assert len(res.json()) == 1 #esto puede cambiar en el contexto de magstats


def test_magstats_with_unknown_survey_id_param(test_client):
    res = test_client.get("/magstats/oid1", params={"survey_id": "unknown"})
    assert "survey id not recognized unknown" in res.json()["detail"]



