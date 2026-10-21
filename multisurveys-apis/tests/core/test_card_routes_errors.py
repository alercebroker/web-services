"""The website cards answer 404 for a missing object and 400 for bad input, not 500 (found by an endpoint sweep)."""

import pytest

from app_client import client_for as api_client


@pytest.fixture
def client_for(db):
    def _client(api):
        return api_client(api, db, raise_server_exceptions=False)

    return _client


@pytest.mark.parametrize(
    "api, path, params, status",
    [
        ("object_api", "/htmx/object_information", {"oid": "abc", "survey_id": "ztf"}, 400),
        ("object_api", "/htmx/object_information", {"oid": "ZTF20aaelulu", "survey_id": "foo"}, 400),
        ("crossmatch_api", "/htmx/crossmatch", {"oid": "ZTF99zzzzzzz", "survey_id": "ztf"}, 404),
        ("crossmatch_api", "/htmx/crossmatch", {"oid": "abc", "survey_id": "ztf"}, 400),
        ("lightcurve_api", "/htmx/external_sources", {"oid": "ZTF20aaelulu", "survey_id": "ztf"}, 400),
        ("object_api", "/htmx/search_objects/", {"survey_id": "foo"}, 400),
    ],
)
def test_card_errors(client_for, api, path, params, status):
    assert client_for(api).get(path, params=params).status_code == status
