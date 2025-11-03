from fastapi.testclient import TestClient


def test_detections_single_oid(client: TestClient, populate_database):
    response = client.get("/detections", params={"survey_id": "lsst", "oid": ["1234"]})
    assert response.status_code == 200


def test_detections_oid_list(client: TestClient, populate_database):
    response = client.get("/detections", params={"survey_id": "lsst", "oid": ["1234", "456"]})
    assert response.status_code == 200
