from returns.result import Success, Failure
from shared.error.exceptions import (
    WrapperException,
)
from shared.utils.result_helpers import get_failure_from_list


def test_wrapper_exception_str(client):
    test_string = "TEST STRING"
    exception = Exception(test_string)
    wrapped_exception = WrapperException(exception)
    assert str(wrapped_exception) == test_string


def test_get_failure_from_list(client):
    results_list = [Success(1), Success(2)]
    assert get_failure_from_list(results_list) is None

    results_list = [Failure(Exception("1")), Success(2)]
    assert str(get_failure_from_list(results_list).failure()) == "1"

    results_list = [Success(1), Failure(Exception("2"))]
    assert str(get_failure_from_list(results_list).failure()) == "2"
