from fastapi.testclient import TestClient


def test_detections(client: TestClient, populate_database):
    response = client.get(
        "/detections", params={"survey_id": "lsst", "oid_list": ["1234"]}
    )
    assert response.status_code == 200
