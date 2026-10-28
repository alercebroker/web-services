"""ZTF magstats keep their band. The JSON rows say it, and the card labels each column by it, not by position."""

import re

import pytest
from db_plugins.db.sql.models_pipeline import LsstDiaObject, MagStat, Object
from sqlalchemy import text

from app_client import client_for
from core.idmapper.idmapper import catalog_oid_to_masterid

R_ONLY = "ZTF20aaaaaaa"
TWO_BANDS = "ZTF20aaaaaab"


@pytest.fixture
def client(db):
    rows = {R_ONLY: [2], TWO_BANDS: [1, 2]}
    with db.session() as session:
        for name in rows:
            oid = catalog_oid_to_masterid("ZTF", name).item()
            session.add(Object(oid=oid, tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        for name, bands in rows.items():
            oid = catalog_oid_to_masterid("ZTF", name).item()
            for band in bands:
                session.add(
                    MagStat(oid=oid, sid=0, band=band, magmean=18.0 + band, n_det=5, firstmjd=60000, lastmjd=60010)
                )
        session.commit()

    yield client_for("magstat_api", db)

    with db.session() as session:
        session.execute(text("DELETE FROM magstat"))
        session.commit()


@pytest.mark.parametrize("name, bands", [(R_ONLY, [2]), (TWO_BANDS, [1, 2])])
def test_json_rows_carry_their_band(client, name, bands):
    response = client.get("/magstats", params={"oid": name, "survey_id": "ztf"})

    assert response.status_code == 200
    assert sorted(row["band"] for row in response.json()) == bands
    assert all("fid" not in row for row in response.json())


def card_columns(html):
    header = html.split("<thead", 1)[1].split("</thead>", 1)[0]
    return [cell.strip() for cell in re.findall(r"<th[^>]*>(.*?)</th>", header, re.S)][1:]  # after "Stat"


def test_card_labels_an_r_only_object_as_r(client):
    response = client.get("/htmx/mag", params={"oid": R_ONLY, "survey_id": "ztf"})

    assert response.status_code == 200
    assert card_columns(response.text) == ["r"]
    assert 'id="row-fid"' not in response.text and 'id="row-band"' not in response.text


def test_card_labels_each_column_by_its_band(client):
    response = client.get("/htmx/mag", params={"oid": TWO_BANDS, "survey_id": "ztf"})
    json_bands = [row["band"] for row in client.get("/magstats", params={"oid": TWO_BANDS, "survey_id": "ztf"}).json()]

    assert card_columns(response.text) == [{1: "g", 2: "r"}[band] for band in json_bands]


@pytest.mark.parametrize("path", ["/magstats", "/htmx/mag"])
def test_survey_is_case_insensitive(client, path):
    response = client.get(path, params={"oid": R_ONLY, "survey_id": "ZTF"})

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/magstats", "/htmx/mag"])
def test_unknown_survey_answers_422(client, path):
    response = client.get(path, params={"oid": R_ONLY, "survey_id": "atlas"})

    assert response.status_code == 422


def test_step_id_corr_is_not_listed(client):
    rows = client.get("/magstats", params={"oid": TWO_BANDS, "survey_id": "ztf"}).json()
    card = client.get("/htmx/mag", params={"oid": TWO_BANDS, "survey_id": "ztf"}).text

    assert all("step_id_corr" not in row for row in rows)
    assert 'id="row-step_id_corr"' not in card


LSST_OID = 170591527609303944


@pytest.fixture
def lsst_client(db):
    with db.session() as session:
        session.add(Object(oid=LSST_OID, tid=1, sid=1, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.commit()
        session.add(LsstDiaObject(oid=LSST_OID, validityStartMjdTai=60000, ra=10.0, dec=10.0, nDiaSources=3))
        session.commit()

    yield client_for("magstat_api", db)

    with db.session() as session:
        session.execute(text("DELETE FROM lsst_dia_object"))
        session.commit()


def test_lsst_card_column_is_all_bands_not_g(lsst_client):
    response = lsst_client.get("/htmx/mag", params={"oid": str(LSST_OID), "survey_id": "lsst"})

    assert response.status_code == 200
    assert card_columns(response.text) == ["All bands"]
