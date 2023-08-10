import requests
from unittest.mock import patch
from returns.pipeline import is_successful
from ralidator_core.users_api_client import UsersApiClient


class MockResponse(object):
    def __init__(self, status, response):
        self.status_code = status
        self.response = response

    def json(self):
        return self.response


TEST_API_URL = "www.users.api"
TEST_API_TOKEN = "test-token"
TEST_FILTERS_LIST = ["filter1", "filter2", "filter3"]


def test_get_all_filters_correct():
    client = UsersApiClient(TEST_API_URL, TEST_API_TOKEN)

    with patch.object(requests, "get") as mock_request:
        mock_request.return_value = MockResponse(200, TEST_FILTERS_LIST)
        result = client.get_all_filters()

        assert is_successful(result)
        assert result.unwrap() == TEST_FILTERS_LIST


def test_get_all_filters_bad_response():
    client = UsersApiClient(TEST_API_URL, TEST_API_TOKEN)

    with patch.object(requests, "get") as mock_request:
        mock_request.return_value = MockResponse(400, {})
        result = client.get_all_filters()

    assert not is_successful(result)
    assert result.failure().code == 400


def test_get_all_filters_forbiden():
    client = UsersApiClient(TEST_API_URL, TEST_API_TOKEN)

    with patch.object(requests, "get") as mock_request:
        mock_request.return_value = MockResponse(403, "")
        result = client.get_all_filters()

    assert not is_successful(result)
    assert result.failure().code == 403


def test_get_all_filters_server_error():
    client = UsersApiClient(TEST_API_URL, TEST_API_TOKEN)

    with patch.object(requests, "get") as mock_request:
        mock_request.return_value = MockResponse(500, "")
        result = client.get_all_filters()

    assert not is_successful(result)
    assert result.failure().code == 500
