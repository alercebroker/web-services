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
        *[
            ("lightcurve_api", "get", path, {"oid": oid, "survey_id": survey})
            for path in ("/detections", "/non_detections", "/forced-photometry", "/lightcurve")
            for oid, survey in ((MISSING_ZTF, "ztf"), (MISSING_LSST, "lsst"))
        ],
    ],
)
def test_missing_object_is_404(client_for, api, method, path, params):
    response = getattr(client_for(api), method)(path, params=params)

    assert response.status_code == 404


def test_lightcurve_docs_say_what_a_missing_oid_answers(client_for):
    parameters = client_for("lightcurve_api").get("/openapi.json").json()["paths"]["/detections"]["get"]["parameters"]
    oid = next(p for p in parameters if p["name"] == "oid")

    assert "With one oid, an object that doesn't exist answers 404" in oid["description"]
    assert "the response doesn't say which" in oid["description"]
