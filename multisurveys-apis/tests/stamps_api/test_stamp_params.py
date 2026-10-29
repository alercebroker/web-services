"""Invalid stamp parameters answer 422 before anything is downloaded; LSST /avro answers 400."""

import importlib
import os

import pytest
from fastapi.testclient import TestClient

from stamps_api.s3_handler.base_handler import BaseS3Handler

STAMP = {"oid": "ZTF18aarwvbm", "measurement_id": "516401801715010008", "survey_id": "ztf"}


@pytest.fixture
def client(monkeypatch):
    # The app builds a database engine at import; these routes never use it, so any settings do
    for name, value in {
        "PSQL_USER": "u",
        "PSQL_PASSWORD": "p",
        "PSQL_DATABASE": "d",
        "PSQL_HOST": "h",
        "PSQL_PORT": "5432",
    }.items():
        if not os.environ.get(name):
            monkeypatch.setenv(name, value)
    app = importlib.import_module("stamps_api.api").app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def s3_download(mocker):
    return mocker.patch.object(BaseS3Handler, "_get_file_from_s3", return_value={})


@pytest.mark.parametrize(
    "params, field",
    [
        ({"stamp_type": "science", "file_format": "png"}, "stamp_type"),
        ({"stamp_type": "cutoutScience", "file_format": "jpg"}, "file_format"),
        ({"stamp_type": "cutoutScience", "file_format": "png", "survey_id": "atlas"}, "survey_id"),
    ],
)
@pytest.mark.parametrize("survey_id", ["ztf", "LSST"])
def test_invalid_stamp_params_are_422_without_download(client, s3_download, params, field, survey_id):
    response = client.get("/stamp", params={**STAMP, "survey_id": survey_id, **params})

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [["query", field]]
    s3_download.assert_not_called()


def test_lsst_avro_is_400(client):
    response = client.get("/avro", params={"oid": "170591527609303944", "measurement_id": "1", "survey_id": "lsst"})

    assert response.status_code == 400
    assert response.json()["detail"] == "The avro of LSST alerts isn't available"
