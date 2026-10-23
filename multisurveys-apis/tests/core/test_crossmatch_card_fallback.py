"""P2-1, the card half: when catsHTM is down or slow, the crossmatch card shows "-" instead of failing.

The JSON /crossmatch keeps answering 502/504 (tests/crossmatch_api/test_catshtm_errors.py).
"""

import pytest
from db_plugins.db.sql.models_pipeline import Object, ZtfObject
from fastapi import HTTPException
from sqlalchemy import text

from app_client import client_for
from core.idmapper.idmapper import catalog_oid_to_masterid

NAME = "ZTF20aaelulu"
NUMBER = catalog_oid_to_masterid("ZTF", NAME).item()
PARAMS = {"oid": NAME, "survey_id": "ztf"}


@pytest.fixture
def client(db):
    with db.session() as session:
        session.add(Object(oid=NUMBER, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        session.add(ZtfObject(oid=NUMBER, stellar=False, corrected=False))
        session.commit()

    yield client_for("crossmatch_api", db, raise_server_exceptions=False)

    with db.session() as session:
        session.execute(text("DELETE FROM ztf_object"))
        session.commit()


@pytest.mark.parametrize("status", [502, 504])
def test_card_shows_the_fallback_when_catshtm_fails(client, mocker, status):
    mocker.patch(
        "crossmatch_api.services.crossmatch_service.get_alerce_data",
        side_effect=HTTPException(status_code=status, detail="catsHTM failed"),
    )

    response = client.get("/htmx/crossmatch", params=PARAMS)

    assert response.status_code == 200
    assert 'id="crossmatch-unavailable"' in response.text


def test_card_has_no_fallback_when_catshtm_answers(client, mocker):
    match = {"AllWISE": {"distance": {"unit": "arcsec", "value": 1.5}, "W1mag": {"unit": "mag", "value": 15.0}}}
    mocker.patch("crossmatch_api.services.crossmatch_service.get_alerce_data", return_value=[match])

    response = client.get("/htmx/crossmatch", params=PARAMS)

    assert response.status_code == 200
    assert 'id="row-AllWISE"' in response.text
    assert 'id="crossmatch-unavailable"' not in response.text


def test_json_still_answers_the_gateway_error(client, mocker):
    mocker.patch(
        "crossmatch_api.services.crossmatch_service.get_alerce_data",
        side_effect=HTTPException(status_code=504, detail="catsHTM failed"),
    )

    assert client.get("/crossmatch", params=PARAMS).status_code == 504
