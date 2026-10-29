"""S3 failures other than a missing file are upstream failures (502/504: S3's fault, not the caller's), not 500."""

import io

import pytest
from botocore.exceptions import ClientError, ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError

from core.exceptions import AlertNotFound, UpstreamTimeout, UpstreamUnavailable

from stamps_api.s3_handler.lsst import LSSTS3Handler
from stamps_api.s3_handler.ztf import ZTFS3Handler


@pytest.fixture(params=[ZTFS3Handler, LSSTS3Handler])
def handler(request, monkeypatch):
    for name in ("ZTF_BUCKET_REGION", "LSST_BUCKET_REGION"):
        monkeypatch.setenv(name, "us-east-1")
    for name in ("ZTF_BUCKET_NAME", "LSST_BUCKET_NAME"):
        monkeypatch.setenv(name, "a-bucket")
    return request.param()


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": code}}, "GetObject")


@pytest.mark.parametrize(
    "failure, error",
    [
        (client_error("AccessDenied"), UpstreamUnavailable),
        (client_error("NoSuchBucket"), UpstreamUnavailable),
        (EndpointConnectionError(endpoint_url="https://s3.amazonaws.com"), UpstreamUnavailable),
        (ConnectTimeoutError(endpoint_url="https://s3.amazonaws.com"), UpstreamTimeout),
        (ReadTimeoutError(endpoint_url="https://s3.amazonaws.com"), UpstreamTimeout),
    ],
)
def test_s3_failures_are_upstream_errors(handler, mocker, failure, error):
    mocker.patch.object(handler.client, "get_object", side_effect=failure)

    with pytest.raises(UpstreamUnavailable) as raised:
        handler._get_file_from_s3("1234")

    assert type(raised.value) is error


def test_a_timeout_while_reading_the_file_is_a_timeout(handler, mocker):
    body = mocker.Mock()
    body.read.side_effect = ReadTimeoutError(endpoint_url="https://s3.amazonaws.com")
    mocker.patch.object(handler.client, "get_object", return_value={"Body": body})

    with pytest.raises(UpstreamTimeout):
        handler._get_file_from_s3("1234")


def test_a_missing_file_is_alert_not_found(handler, mocker):
    missing = handler.client.exceptions.NoSuchKey({"Error": {"Code": "NoSuchKey", "Message": "x"}}, "GetObject")
    mocker.patch.object(handler.client, "get_object", side_effect=missing)

    with pytest.raises(AlertNotFound):
        handler._get_file_from_s3("1234")


def test_a_good_file_is_read(handler, mocker):
    mocker.patch.object(handler.client, "get_object", return_value={"Body": io.BytesIO(b"x")})
    mocker.patch("stamps_api.s3_handler.base_handler.reader", return_value=iter([{"ok": True}]))

    assert handler._get_file_from_s3("1234") == {"ok": True}


def test_the_s3_client_has_timeouts_and_bounded_retries(handler):
    config = handler.client.meta.config
    assert config.connect_timeout == 5
    assert config.read_timeout == 15
    assert config.retries == {"total_max_attempts": 2, "mode": "standard"}
