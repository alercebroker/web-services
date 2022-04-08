from flask import g
import logging


def test_before_request(psql_service, client_app):
    client, app = client_app
    with app.test_request_context("/"):
        app.preprocess_request()
        assert g.time is not None


def test_after_request(caplog, psql_service, client_app):
    client, app = client_app
    caplog.set_level(logging.DEBUG)
    with app.test_request_context("/"):
        app.preprocess_request()
        rv = app.dispatch_request()
        res = app.make_response(rv)
        app.process_response(res)
        assert "GET http /? 200 OK time:" in caplog.text
