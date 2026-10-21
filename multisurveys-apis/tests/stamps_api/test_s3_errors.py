"""S3 failures other than a missing file answer 502/504 (S3's fault, not the caller's), not 500."""

import io

import pytest
from botocore.exceptions import ClientError, ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError
from fastapi import HTTPException

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
    "failure, status",
    [
        (client_error("AccessDenied"), 502),
        (client_error("NoSuchBucket"), 502),
        (EndpointConnectionError(endpoint_url="https://s3.amazonaws.com"), 502),
        (ConnectTimeoutError(endpoint_url="https://s3.amazonaws.com"), 504),
        (ReadTimeoutError(endpoint_url="https://s3.amazonaws.com"), 504),
    ],
)
def test_s3_failures_are_gateway_errors(handler, mocker, failure, status):
    mocker.patch.object(handler.client, "get_object", side_effect=failure)

    with pytest.raises(HTTPException) as raised:
        handler._get_file_from_s3("1234")

    assert raised.value.status_code == status


def test_a_timeout_while_reading_the_file_is_504(handler, mocker):
    body = mocker.Mock()
    body.read.side_effect = ReadTimeoutError(endpoint_url="https://s3.amazonaws.com")
    mocker.patch.object(handler.client, "get_object", return_value={"Body": body})

    with pytest.raises(HTTPException) as raised:
        handler._get_file_from_s3("1234")

    assert raised.value.status_code == 504


def test_a_missing_file_is_still_404(handler, mocker):
    missing = handler.client.exceptions.NoSuchKey({"Error": {"Code": "NoSuchKey", "Message": "x"}}, "GetObject")
    mocker.patch.object(handler.client, "get_object", side_effect=missing)

    with pytest.raises(HTTPException) as raised:
        handler._get_file_from_s3("1234")

    assert raised.value.status_code == 404


def test_a_good_file_is_read(handler, mocker):
    mocker.patch.object(handler.client, "get_object", return_value={"Body": io.BytesIO(b"x")})
    mocker.patch("stamps_api.s3_handler.base_handler.reader", return_value=iter([{"ok": True}]))

    assert handler._get_file_from_s3("1234") == {"ok": True}
