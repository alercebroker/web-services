from fastapi.testclient import TestClient


def test_conesearch(client: TestClient):
    response = client.get("/conesearch", params={"oid": "1"})
    assert response.status_code == 200
