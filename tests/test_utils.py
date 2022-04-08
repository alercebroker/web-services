from logging import exception
from unittest.mock import patch
import pytest
from returns.result import Success, Failure
from api.result_handlers.exceptions import (
    WrapperException,
    ClientErrorException,
    ServerErrorException,
    InterfaceNotFound,
    ObjectNotFound,
)
from api.result_handlers.helper_functions import get_failure_from_list


def test_wrapper_exception_str(mongo_service, psql_service, client):
    test_string = "TEST STRING"
    exception = Exception(test_string)
    wrapped_exception = WrapperException(exception)
    assert str(wrapped_exception) == test_string

def test_interface_not_found_str(mongo_service, psql_service, client):
    exception = InterfaceNotFound("Error")
    assert str(exception) == "Interface not found for Error" 

def test_object_not_found_str(mongo_service, psql_service, client):
    exception = ObjectNotFound(1, "Error")
    assert str(exception) == "Object 1 Not Found in survey Error" 

def test_get_failure_from_list(mongo_service, psql_service, client):
    results_list = [
        Success(1),
        Success(2)
    ]
    assert get_failure_from_list(results_list) == None

    results_list = [
        Failure(Exception("1")),
        Success(2)
    ]
    assert str(get_failure_from_list(results_list).failure()) == "1"

    results_list = [
        Success(1),
        Failure(Exception("2"))
    ]
    assert str(get_failure_from_list(results_list).failure()) == "2"