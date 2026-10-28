"""Every API serves Prometheus metrics at /metrics, since the chart marks all their services for scraping."""

import pytest

from app_client import client_for

APIS = [
    "lightcurve_api",
    "object_api",
    "magstat_api",
    "probability_api",
    "classifier_api",
    "crossmatch_api",
    "stamps_api",
    "aladin_api",
    "features_api",
    "status_api",
]


@pytest.mark.parametrize("api", APIS)
def test_metrics_are_served(db, api):
    client = client_for(api)
    client.get("/")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text


@pytest.mark.parametrize("api", APIS)
def test_metrics_are_not_listed_in_the_docs(db, api):
    assert "/metrics" not in client_for(api).get("/openapi.json").json()["paths"]
