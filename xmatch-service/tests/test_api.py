from fastapi.testclient import TestClient
import pytest
import os
from healpy.pixelfunc import ang2pix

@pytest.fixture
def env_setup():
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "postgres"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_DATABASE"] = "postgres"
    yield
    os.environ.pop("DB_USER")
    os.environ.pop("DB_PASSWORD")
    os.environ.pop("DB_HOST")
    os.environ.pop("DB_PORT")
    os.environ.pop("DB_DATABASE")

@pytest.fixture
def test_client(env_setup):
    def _client():
        from api.api import app, pool
        client = TestClient(app)
        return client, pool
    return _client



def test_conesearch(init_database, test_client):
    client, pool = test_client()
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (oid, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipix = int(ang2pix(2**14, 1.0, 1.0, lonlat=True))
            cur.execute(query, ("1", ipix, 1.0, 1.0, "wise"))
            cur.execute(query, ("2", ipix, 1.0, 1.0, "vlass"))
            cur.execute(query, ("3", ipix, 1.0, 1.0, "lsdr10"))
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1&cat=all")
    assert response.status_code == 200
    assert response.json() == ["1", "2", "3"]
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1&cat=wise")
    assert response.status_code == 200
    assert response.json() == ["1"]
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1&cat=vlass")
    assert response.status_code == 200
    assert response.json() == ["2"]
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1&cat=lsdr10")
    assert response.status_code == 200
    assert response.json() == ["3"]
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1&cat=unknown")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "literal_error"
    assert response.json()["detail"][0]["loc"] == ["query", "cat"]
    assert response.json()["detail"][0]["msg"] == "Input should be 'all', 'wise', 'vlass' or 'lsdr10'"
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=1")
    assert response.status_code == 200
    assert response.json() == ["1", "2", "3"]
    response = client.get("/conesearch?ra=1.0&dec=1.0&radius=0")
    assert response.status_code == 422
    
