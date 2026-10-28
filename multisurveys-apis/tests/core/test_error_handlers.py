import asyncio

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.error_handlers import add_error_handlers
from core.exceptions import DatabaseError, ObjectNotFound


def make_app() -> CORSMiddleware:
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/ok")
    def ok():
        return "ok"

    @app.get("/not-found")
    def not_found():
        raise ObjectNotFound("ZTF00abc")

    @app.get("/db-error")
    def db_error():
        raise DatabaseError(RuntimeError("connection reset"), database="psql")

    @app.get("/bad-value")
    def bad_value():
        raise ValueError("n_det must be positive")

    @app.get("/timeout-operational")
    def timeout_operational():
        raise Exception("(psycopg2.errors.QueryCanceled) canceling statement due to statement timeout")  # noqa: TRY002

    @app.get("/timeout-wrapped")
    def timeout_wrapped():
        raise Exception("statement timeout")  # noqa: TRY002

    @app.get("/unexpected")
    def unexpected():
        raise RuntimeError("something broke")

    class Row(BaseModel):
        stellar: bool

    @app.get("/bad-row")
    def bad_row():
        return Row(stellar=None)

    @app.get("/typed")
    def typed(n: int):
        return n

    return CORSMiddleware(app, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def _get(path, origin="https://explorer.alerce.online"):
    app = make_app()
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    async def run():
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path, headers={"Origin": origin} if origin else {})

    return asyncio.run(run())


def test_object_not_found_returns_404():
    r = _get("/not-found")
    assert r.status_code == 404
    assert r.json() == {"detail": "Object ZTF00abc not found on the database"}


def test_database_error_returns_500():
    r = _get("/db-error")
    assert r.status_code == 500
    assert r.json() == {"detail": "Database error"}


def test_value_error_returns_400():
    r = _get("/bad-value")
    assert r.status_code == 400
    assert r.json() == {"detail": "n_det must be positive"}


def test_timeout_from_operational_error_message_returns_504():
    r = _get("/timeout-operational")
    assert r.status_code == 504
    assert r.json() == {"detail": "Query timed out"}


def test_timeout_from_wrapped_exception_returns_504():
    r = _get("/timeout-wrapped")
    assert r.status_code == 504
    assert r.json() == {"detail": "Query timed out"}


def test_unexpected_error_returns_500():
    r = _get("/unexpected")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error"}


def test_validation_error_in_our_own_models_returns_500():
    r = _get("/bad-row")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error"}


def test_bad_request_parameter_still_returns_422():
    r = _get("/typed?n=abc")
    assert r.status_code == 422


def test_success_still_works():
    r = _get("/ok")
    assert r.status_code == 200


def test_error_responses_carry_cors_headers():
    # allow_credentials=True: Starlette 1.x echoes the caller's origin instead of "*"
    origin = "https://explorer.alerce.online"

    r = _get("/not-found", origin)
    assert r.headers["access-control-allow-origin"] == origin

    r = _get("/timeout-operational", origin)
    assert r.headers["access-control-allow-origin"] == origin

    r = _get("/unexpected", origin)
    assert r.headers["access-control-allow-origin"] == origin
