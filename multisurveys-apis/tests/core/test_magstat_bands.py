"""P1-3: ZTF magstats keep their band. The JSON rows say it, and the card labels each column by it, not by position."""

import re

import pytest
from db_plugins.db.sql.models_pipeline import MagStat, Object
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
