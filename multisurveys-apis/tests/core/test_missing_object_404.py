"""A missing object answers 404, not 500, on every API that looks one up."""

import pytest

from app_client import client_for as api_client

MISSING_ZTF = "ZTF99zzzzzzz"
MISSING_LSST = "1"


@pytest.fixture
def client_for(db):
    def _client(api):
        return api_client(api, db, raise_server_exceptions=False)

    return _client


@pytest.mark.parametrize(
    "api, method, path, params",
    [
        ("object_api", "get", "/object", {"oid": MISSING_ZTF, "survey_id": "ztf"}),
        ("object_api", "get", "/object", {"oid": MISSING_LSST, "survey_id": "lsst"}),
        ("object_api", "get", "/htmx/object_information", {"oid": MISSING_ZTF, "survey_id": "ztf"}),
        ("crossmatch_api", "get", "/crossmatch", {"oid": MISSING_ZTF, "survey_id": "ztf"}),
        ("magstat_api", "get", "/magstats", {"oid": MISSING_ZTF, "survey_id": "ztf"}),
        ("magstat_api", "get", "/magstats", {"oid": MISSING_LSST, "survey_id": "lsst"}),
        ("magstat_api", "get", "/htmx/mag", {"oid": MISSING_ZTF, "survey_id": "ztf"}),
        ("magstat_api", "get", "/htmx/mag", {"oid": MISSING_LSST, "survey_id": "lsst"}),
    ],
)
def test_missing_object_is_404(client_for, api, method, path, params):
    response = getattr(client_for(api), method)(path, params=params)

    assert response.status_code == 404
