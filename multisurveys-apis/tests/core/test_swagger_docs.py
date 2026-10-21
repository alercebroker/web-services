"""SW-1: the /docs page of each API (the 8, and features) loads its OpenAPI schema from behind the nginx prefix.

nginx strips /<api>_api before forwarding, so these requests use the stripped paths, as the app sees them in
production. /docs must then ask for /<api>_api/openapi.json (the browser goes through the prefix), and the
schema's server must be /<api>_api so "Try it out" also goes through it. Static files must keep loading.
"""

import pytest

from app_client import client_for as api_client

# (api, a static file the app serves, as nginx forwards it)
APIS = [
    ("lightcurve_api", "/static/lightcurve-app.js"),
    ("object_api", "/htmx/htmx.min.js"),
    ("magstat_api", "/htmx-static/htmx.min.js"),
    ("probability_api", "/htmx/htmx.min.js"),
    ("classifier_api", None),
    ("crossmatch_api", "/htmx/htmx.min.js"),
    ("stamps_api", "/htmx-static/htmx.min.js"),
    ("aladin_api", "/htmx/htmx.min.js"),
    ("features_api", None),
]


@pytest.fixture
def client_for(db):
    def _client(api):
        return api_client(api)

    return _client


@pytest.mark.parametrize("api, _", APIS)
def test_docs_page_asks_for_the_schema_through_the_prefix(client_for, api, _):
    response = client_for(api).get("/docs")

    assert response.status_code == 200
    assert f"'/{api}/openapi.json'" in response.text


@pytest.mark.parametrize("api, _", APIS)
def test_schema_lists_the_endpoints_and_the_prefixed_server(client_for, api, _):
    response = client_for(api).get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert len(schema["paths"]) > 0
    assert schema["servers"] == [{"url": f"/{api}"}]


@pytest.mark.parametrize("api, static_file", [(api, f) for api, f in APIS if f])
def test_static_files_still_load(client_for, api, static_file):
    assert client_for(api).get(static_file).status_code == 200
