"""The status API's /docs asks for its schema through the nginx prefix (/status_api), like the other APIs."""

from fastapi.testclient import TestClient

from status_api.api import app


def test_docs_asks_for_the_schema_through_the_prefix():
    response = TestClient(app).get("/docs")

    assert response.status_code == 200
    assert "'/status_api/openapi.json'" in response.text


def test_schema_server_is_the_prefix():
    schema = TestClient(app).get("/openapi.json").json()

    assert schema["servers"] == [{"url": "/status_api"}]
    assert "/pipeline_status" in schema["paths"]
