from db_plugins.db.sql.models_pipeline import ZtfForcedPhotometry
from fastapi.testclient import TestClient
from sqlalchemy import select

N_POINTS = 12  # more than the old .limit(10) on the single-oid queries


def _ztf_oid_with_points(db_setup) -> int:
    with db_setup.session() as session:
        return session.execute(select(ZtfForcedPhotometry.oid).limit(1)).scalar_one()


def test_ztf_forced_photometry_single_oid(client: TestClient, populate_database, db_setup):
    populate_database(N_POINTS)
    oid = _ztf_oid_with_points(db_setup)

    response = client.get("/forced-photometry", params={"survey_id": "ztf", "oid": [str(oid)]})

    assert response.status_code == 200
    assert len(response.json()) == N_POINTS


def test_ztf_non_detections_single_oid_returns_every_row(client: TestClient, populate_database, db_setup):
    populate_database(N_POINTS)
    oid = _ztf_oid_with_points(db_setup)

    response = client.get("/non_detections", params={"survey_id": "ztf", "oid": [str(oid)]})

    assert response.status_code == 200
    assert len(response.json()) == N_POINTS


def test_ztf_lightcurve_single_oid(client: TestClient, populate_database, db_setup):
    populate_database(N_POINTS)
    oid = _ztf_oid_with_points(db_setup)

    response = client.get("/lightcurve", params={"survey_id": "ztf", "oid": [str(oid)]})

    assert response.status_code == 200
    body = response.json()
    assert len(body["detections"]) == N_POINTS
    assert len(body["non_detections"]) == N_POINTS
    assert len(body["forced_photometry"]) == N_POINTS
