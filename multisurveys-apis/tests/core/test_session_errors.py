"""Errors raised inside a database session reach the handlers as themselves, and /metrics counts them by status."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy import text

from db_plugins.db.sql.models_pipeline import Object

from app_client import client_for
from core.error_handlers import add_error_handlers
from core.idmapper import idmapper
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

    @app.get("/timeout")
    def timeout():
        with db.session() as session:
            session.execute(text("SET statement_timeout = 1"))
            session.execute(text("SELECT pg_sleep(1)"))

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
        ("/timeout", 504, "Query timed out"),
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


def test_a_query_timeout_is_not_re_raised_as_an_unhandled_error(client):
    # Starlette re-raises whatever reaches the Exception handler; this client raises it too
    response = TestClient(client.app).get("/timeout")

    assert response.status_code == 504


def test_aladin_object_missing_a_field_is_400(db):
    oid = idmapper.catalog_oid_to_masterid("ZTF", "ZTF18abbrrty").item()
    with db.session() as session:
        session.add(Object(oid=oid, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
    client = client_for("aladin_api", db, raise_server_exceptions=False)

    response = client.post(
        "/htmx/aladin",
        params={"oid": "ZTF18abbrrty", "survey": "ztf"},
        data={"objects_arr": "[{'oid': 'ZTF18abbrrty', 'sid': 0}]"},
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith("objects_arr has an invalid object (meanra, meandec)")
