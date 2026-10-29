import json

import pytest
import requests

from crossmatch_api import get_crossmatch_data
from crossmatch_api.get_crossmatch_data import CATSHTM_TIMEOUT, get_alerce_data
from core.exceptions import UpstreamTimeout, UpstreamUnavailable


def fake_response(status_code=200, body=b"[]"):
    response = requests.Response()
    response.status_code = status_code
    response._content = body
    return response


def test_success_returns_the_matches_and_sets_a_timeout(mocker):
    get = mocker.patch.object(
        get_crossmatch_data.requests, "get", return_value=fake_response(body=json.dumps([{"AllWISE": {}}]).encode())
    )

    assert get_alerce_data(150.1, 2.2, 20) == [{"AllWISE": {}}]
    assert get.call_args.kwargs["timeout"] == CATSHTM_TIMEOUT


@pytest.mark.parametrize(
    "failure, error",
    [
        (requests.ConnectTimeout("connect timed out"), UpstreamTimeout),
        (requests.ReadTimeout("read timed out"), UpstreamTimeout),
        (requests.ConnectionError("refused"), UpstreamUnavailable),
    ],
)
def test_transport_failures_are_upstream_errors(mocker, failure, error):
    mocker.patch.object(get_crossmatch_data.requests, "get", side_effect=failure)

    with pytest.raises(UpstreamUnavailable) as raised:
        get_alerce_data(150.1, 2.2, 20)
    assert type(raised.value) is error


@pytest.mark.parametrize("response", [fake_response(status_code=500), fake_response(body=b"<html>not json</html>")])
def test_bad_upstream_answers_are_502(mocker, response):
    # Before 0.2.11 these returned an "Error: ..." string where a list was expected, which became a 500.
    mocker.patch.object(get_crossmatch_data.requests, "get", return_value=response)

    with pytest.raises(UpstreamUnavailable) as raised:
        get_alerce_data(150.1, 2.2, 20)
    assert type(raised.value) is UpstreamUnavailable
