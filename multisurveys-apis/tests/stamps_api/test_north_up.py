"""LSST stamps can be rotated to North up / East left, and the htmx card toggles that."""

import gzip
import importlib
import io
import json
import os

import astropy.io.fits as fio
import numpy as np
import pytest
from astropy.wcs import WCS
from fastapi.testclient import TestClient
from matplotlib.transforms import Affine2D

from stamps_api.s3_handler.base_handler import BaseS3Handler
from stamps_api.s3_handler.fits_to_png import north_up_angle, transform

# PC matrices of three epochs of one LSST object, a visit apart: Rubin's mount left them 177°, 102° and 84° from North
LSST_PCS = [
    (5.5434369224538e-05, -3.130235275934e-06, -3.1897096854993e-06, -5.547971827582e-05),
    (1.1446749049781e-05, -5.4295256589524e-05, -5.4357808139434e-05, -1.1378996486185e-05),
    (-5.3814841731273e-06, -5.5273416345709e-05, -5.5303609560256e-05, 5.4364600056149e-06),
]


def lsst_header(pc):
    # Like LSST cutouts: PC + CDELT, no CTYPE
    header = fio.Header()
    header["CRPIX1"], header["CRPIX2"] = 15.5, 15.2
    header["CRVAL1"], header["CRVAL2"] = 11.06, -43.34
    header["CDELT1"], header["CDELT2"] = 1.0, 1.0
    header["PC1_1"], header["PC1_2"], header["PC2_1"], header["PC2_2"] = pc
    return header


@pytest.mark.parametrize("pc", LSST_PCS)
def test_rotation_puts_north_up_and_east_left(pc):
    header = lsst_header(pc)
    wcs_header = header.copy()
    wcs_header["CTYPE1"], wcs_header["CTYPE2"] = "RA---TAN", "DEC--TAN"
    wcs = WCS(wcs_header)
    ra, dec, arcsec = header["CRVAL1"], header["CRVAL2"], 1 / 3600
    points = wcs.world_to_pixel_values(
        [ra, ra, ra + arcsec / np.cos(np.radians(dec))],
        [dec, dec + arcsec, dec],
    )

    rotation = Affine2D().rotate_deg_around(header["CRPIX1"] - 1, header["CRPIX2"] - 1, north_up_angle(header))
    center, north, east = rotation.transform(np.array(points).T)

    np.testing.assert_allclose(north - center, [0, 5], atol=0.05)  # 0.2"/pix
    np.testing.assert_allclose(east - center, [-5, 0], atol=0.05)


def test_a_stamp_without_wcs_has_no_angle():
    assert north_up_angle(fio.Header()) is None


def make_fits(header) -> bytes:
    rng = np.random.default_rng(1)
    data = rng.normal(100, 10, size=(30, 30)).astype(np.float32)
    data[5:9, 20:24] += 300  # off-centre, so a rotation changes the image
    buf = io.BytesIO()
    fio.PrimaryHDU(data, header=header).writeto(buf)
    return buf.getvalue()


def test_north_up_rotates_a_stamp_with_wcs():
    fits = make_fits(lsst_header(LSST_PCS[1]))

    assert transform(fits, "cutoutScience", 2, False, north_up=True) != transform(fits, "cutoutScience", 2, False)


def test_north_up_leaves_a_stamp_without_wcs_alone():
    fits = gzip.compress(make_fits(fio.Header()))

    assert transform(fits, "cutoutScience", 2, True, north_up=True) == transform(fits, "cutoutScience", 2, True)


@pytest.fixture
def client(monkeypatch):
    # The app builds a database engine at import; the POST route never uses it, so any settings do
    for name, value in {
        "PSQL_USER": "u",
        "PSQL_PASSWORD": "p",
        "PSQL_DATABASE": "d",
        "PSQL_HOST": "h",
        "PSQL_PORT": "5432",
        "LSST_BUCKET_REGION": "us-east-1",
    }.items():
        if not os.environ.get(name):
            monkeypatch.setenv(name, value)
    app = importlib.import_module("stamps_api.api").app
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize("north_up", [True, False])
def test_the_card_renders_the_requested_orientation_and_offers_the_other(client, mocker, north_up):
    stamp = {"file_name": "x", "file": b"x", "mime": "image/png"}
    stamps = {f: {t: stamp for t in ["cutoutScience", "cutoutTemplate", "cutoutDifference"]} for f in ["png", "fits"]}
    get_all_stamps = mocker.patch.object(BaseS3Handler, "get_all_stamps", return_value=stamps)
    detections = [{"mjd": 1.0, "greg": "2026-01-01", "measurement_id": "7", "band": "g", "has_stamp": True}]

    # As the card's controls send it: a form field holding JSON (see stampPayload in stamps_layout)
    payload = {
        "oid": "1",
        "survey_id": "lsst",
        "measurement_id": "7",
        "detections_list": detections,
        "north_up": north_up,
    }
    response = client.post("/htmx/update_stamp_card", data={"payload": json.dumps(payload)})

    assert response.status_code == 200
    assert get_all_stamps.call_args.kwargs["north_up"] is north_up
    assert f'data-north-up="{str(not north_up).lower()}"' in response.text


@pytest.mark.parametrize("data", [{}, {"payload": "not json"}, {"payload": json.dumps({"oid": "1"})}])
def test_a_bad_update_payload_is_422(client, mocker, data):
    get_all_stamps = mocker.patch.object(BaseS3Handler, "get_all_stamps")

    response = client.post("/htmx/update_stamp_card", data=data)

    assert response.status_code == 422
    get_all_stamps.assert_not_called()
