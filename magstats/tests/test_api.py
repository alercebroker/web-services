def test_root(test_client):
    res = test_client.get("/")
    assert res.status_code == 200



def test_magstats_from_ztf(psql_service, init_psql, test_client):
    res = test_client.get("/magstats/oid1")
    assert res.status_code == 200
    assert res.json()[0]['fid'] == 123 


def test_magstats_with_unknown_oid_param(test_client): # este tiene problemas y no se pq
    res = test_client.get("/magstats/oid1")
    print("-------------a------------------")
    print(res.json())
    #assert False
    assert "oid not recognized unknown" in res.json()["detail"]



