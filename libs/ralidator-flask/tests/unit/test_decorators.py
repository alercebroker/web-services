from ralidator_flask.decorators import (
    set_filters_decorator,
    set_permissions_decorator,
    check_permissions_decorator,
)
from unittest.mock import patch
from ralidator_flask.ralidator_flask import Ralidator


def test_set_filters_decorator(ralidator_flask, app):
    @set_filters_decorator(["test"])
    def function():
        pass

    with patch.object(Ralidator, "set_app_filters") as ralidator_mock:
        with app.test_request_context():
            ralidator_flask.set_ralidator_on_context()
            function()
            ralidator_mock.assert_called_with(["test"])


def test_set_permissions_decorator(ralidator_flask, app):
    @set_permissions_decorator(["test"])
    def function():
        pass

    with patch.object(Ralidator, "set_required_permissions") as ralidator_mock:
        with app.test_request_context():
            ralidator_flask.set_ralidator_on_context()
            function()
            ralidator_mock.assert_called_with(["test"])


def test_check_permissions_decorator(ralidator_flask, app):
    @check_permissions_decorator
    def function():
        pass

    with patch.object(Ralidator, "check_if_allowed") as ralidator_mock:
        ralidator_mock.return_value = True, None
        with app.test_request_context():
            ralidator_flask.set_ralidator_on_context()
            function()
            ralidator_mock.assert_called()
