"""Errors raised inside a database session reach the handlers as themselves, and /metrics counts them by status."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from core.error_handlers import add_error_handlers
from core.exceptions import ObjectNotFound


class Row(BaseModel):
    stellar: bool


@pytest.fixture
def client(db):
    app = FastAPI()
    add_error_handlers(app)
    Instrumentator(registry=CollectorRegistry()).instrument(app).expose(app)

    @app.get("/not-found")
    def not_found():
        with db.session():
            raise ObjectNotFound("ZTF00abc")

    @app.get("/bad-value")
    def bad_value():
        with db.session():
            raise ValueError("Unsupported survey: atlas")

    @app.get("/bad-row")
    def bad_row():
        with db.session():
            Row(stellar=None)

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    "path, status, detail",
    [
        ("/not-found", 404, "Object ZTF00abc not found on the database"),
        ("/bad-value", 400, "Unsupported survey: atlas"),
        ("/bad-row", 500, "Internal server error"),
    ],
)
def test_errors_inside_a_session_answer_their_own_status(client, path, status, detail):
    response = client.get(path)

    assert response.status_code == status
    assert response.json() == {"detail": detail}


def test_client_errors_inside_a_session_are_counted_as_4xx(client):
    client.get("/not-found")
    client.get("/bad-value")

    metrics = client.get("/metrics").text

    assert 'handler="/not-found",method="GET",status="4xx"' in metrics
    assert 'handler="/bad-value",method="GET",status="4xx"' in metrics
    assert 'status="5xx"' not in metrics
