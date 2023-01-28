from ralidator_fastapi.decorators import (
    set_filters_decorator,
    set_permissions_decorator,
    check_permissions_decorator,
)
from pytest_mock.plugin import MockerFixture


def test_set_filters_decorator(mocker: MockerFixture):
    get_ralidator = mocker.patch("ralidator_fastapi.decorators.get_ralidator")

    @set_filters_decorator(["a", "b"])
    def decorated():
        return 1

    res = decorated()
    assert res == 1
    get_ralidator.assert_called()
    get_ralidator.return_value.set_app_filters.assert_called_with(["a", "b"])


def test_set_permissions_decorator(mocker: MockerFixture):
    get_ralidator = mocker.patch("ralidator_fastapi.decorators.get_ralidator")

    @set_permissions_decorator(["a", "b"])
    def decorated():
        return 1

    res = decorated()
    assert res == 1
    get_ralidator.assert_called()
    get_ralidator.return_value.set_required_permissions.assert_called_with(["a", "b"])


def test_check_permissions_decorator_forbidden(mocker: MockerFixture):
    get_ralidator = mocker.patch("ralidator_fastapi.decorators.get_ralidator")
    get_ralidator.return_value.check_if_allowed.return_value = (False, 403)

    @check_permissions_decorator
    def decorated():
        return 1, 2

    res = decorated()
    assert res[0] == "Forbidden"
    assert res[1] == 403


def test_check_permissions_decorator_allowed(mocker: MockerFixture):
    get_ralidator = mocker.patch("ralidator_fastapi.decorators.get_ralidator")
    get_ralidator.return_value.check_if_allowed.return_value = (True, 1)

    @check_permissions_decorator
    def decorated():
        return 1, 2

    res = decorated()
    assert res[0] == 1
    assert res[1] == 2


def test_check_permissions_decorator_expired(mocker: MockerFixture):
    get_ralidator = mocker.patch("ralidator_fastapi.decorators.get_ralidator")
    get_ralidator.return_value.check_if_allowed.return_value = (False, 401)

    @check_permissions_decorator
    def decorated():
        return 1, 2

    res = decorated()
    assert res[0] == "Expired Token"
    assert res[1] == 401
