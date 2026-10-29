"""The stamp card renders a message when S3 fails, and downloads each alert once for png and fits."""

import gzip
import io

import astropy.io.fits as fio
import numpy as np
import pytest

from app_client import client_for
from core.exceptions import AlertNotFound, UpstreamTimeout, UpstreamUnavailable
from stamps_api.s3_handler.ztf import ZTFS3Handler

DETECTIONS = [
    {"mjd": 60000.0, "greg": "2023-02-25", "measurement_id": "111", "band": "g", "has_stamp": True},
    {"mjd": 60001.0, "greg": "2023-02-26", "measurement_id": "222", "band": "r", "has_stamp": True},
]
BODY = {"oid": "ZTF20aaelulu", "survey_id": "ztf", "measurement_id": 111, "detections_list": DETECTIONS}


def fits() -> bytes:
    buf = io.BytesIO()
    fio.PrimaryHDU(np.random.default_rng(1).normal(100, 10, size=(63, 63)).astype(np.float32)).writeto(buf)
    return gzip.compress(buf.getvalue())


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setenv("ZTF_BUCKET_REGION", "us-east-1")
    monkeypatch.setenv("ZTF_BUCKET_NAME", "a-bucket")
    return client_for("stamps_api", db, raise_server_exceptions=False)


@pytest.mark.parametrize("error", [AlertNotFound, UpstreamUnavailable, UpstreamTimeout])
def test_card_says_the_stamps_are_unavailable_when_s3_fails(client, mocker, error):
    mocker.patch.object(ZTFS3Handler, "_get_file_from_s3", side_effect=error("S3 failed"))

    response = client.post("/htmx/update_stamp_card", json=BODY)

    assert response.status_code == 200
    assert 'id="stamps-unavailable"' in response.text
    assert "2023-02-26" in response.text


def test_card_downloads_the_alert_once_for_png_and_fits(client, mocker):
    avro = {stamp: {"stampData": fits()} for stamp in ("cutoutScience", "cutoutTemplate", "cutoutDifference")}
    download = mocker.patch.object(ZTFS3Handler, "_get_file_from_s3", return_value=avro)

    response = client.post("/htmx/update_stamp_card", json=BODY)

    assert response.status_code == 200
    assert download.call_count == 1
    assert 'id="stamps-unavailable"' not in response.text
    assert "data:image/png;base64" in response.text
    assert "data:application/gzip;base64" in response.text
