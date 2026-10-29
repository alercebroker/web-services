"""Lists of oids take at most MAX_OIDS_PER_REQUEST ids, like the explorer's search."""

import pytest

from app_client import client_for
from core.idmapper.idmapper import MAX_OIDS_PER_REQUEST

OIDS = [str(i) for i in range(1, MAX_OIDS_PER_REQUEST + 2)]


@pytest.mark.parametrize(
    "api, path, params",
    [
        ("object_api", "/list_objects", {"survey": "lsst"}),
        ("lightcurve_api", "/detections", {"survey_id": "lsst"}),
        ("lightcurve_api", "/non_detections", {"survey_id": "lsst"}),
        ("lightcurve_api", "/forced-photometry", {"survey_id": "lsst"}),
        ("lightcurve_api", "/lightcurve", {"survey_id": "lsst"}),
    ],
)
@pytest.mark.parametrize("count, status", [(MAX_OIDS_PER_REQUEST, 200), (MAX_OIDS_PER_REQUEST + 1, 422)])
def test_oid_lists_are_limited(db, api, path, params, count, status):
    response = client_for(api, db, raise_server_exceptions=False).get(path, params={**params, "oid": OIDS[:count]})

    assert response.status_code == status
    if status == 422:
        assert response.json()["detail"][0]["loc"] == ["query", "oid"]
