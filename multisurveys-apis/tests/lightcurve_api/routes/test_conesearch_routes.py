from core.idmapper.idmapper import catalog_oid_to_masterid
from db_plugins.db.sql.models import Object
from fastapi.testclient import TestClient
from sqlalchemy import select


def test_conesearch_objects(client: TestClient, populate_database):
    populate_database(100)
    response = client.get(
        "/conesearch/objects_by_oid",
        params={
            "oid": "ZTF20aaelulu",
            "survey": "ZTF",
            "radius": "30",
            "neighbors": "10",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_conesearch_objects_invalid_params(client: TestClient):
    params = [
        {
            "oid": "invalid_object",
            "survey": "ZTF",
            "radius": "30",
            "neighbors": "10",
        },
        {
            "oid": "ZTF20aaelulu",
            "survey": "invalid_survey",
            "radius": "30",
            "neighbors": "10",
        },
        {
            "oid": "ZTF20aaelulu",
            "survey": "ZTF",
            "radius": "-5",
            "neighbors": "10",
        },
        {
            "oid": "ZTF20aaelulu",
            "survey": "ZTF",
            "radius": "30",
            "neighbors": "0",
        },
        {
            "oid": "ZTF20aaelulu",
            "survey": "ZTF",
            "radius": "text",
            "neighbors": "1",
        },
    ]
    expected = [
        (
            lambda x: x["detail"] == "Invalid ZTF object ID: invalid_object",
            400,
        ),
        (
            lambda x: x["detail"] == "Unsupported catalog: INVALID_SURVEY",
            400,
        ),
        (lambda x: x["detail"] == "Radius must be greater than 0", 400),
        (lambda x: x["detail"] == "Neighbors must be greater than 0", 400),
        (
            lambda x: x["detail"][0]["msg"]
            == "Input should be a valid number, unable to parse string as a number",
            422,
        ),
    ]
    for param, exp in zip(params, expected):
        response = client.get(
            "/conesearch/objects_by_oid",
            params=param,
        )
        assert response.status_code == exp[1], param
        assert exp[0](response.json())


def test_conesearch_coordinates(client: TestClient, populate_database, db_setup):
    populate_database(100)
    # find known object
    with db_setup.session() as session:
        id = catalog_oid_to_masterid("ZTF", "ZTF20aaelulu", True)
        obj = (
            session.execute(select(Object).where(Object.oid == id.item()))
            .scalars()
            .first()
        )

    response = client.get(
        "/conesearch/objects_by_coordinates",
        params={
            "ra": str(obj.meanra),
            "dec": str(obj.meandec),
            "radius": "30",
            "neighbors": "10",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_oid_lightcurve(client: TestClient, populate_database):
    populate_database(100)
    response = client.get(
        "/conesearch/lightcurve_by_oid",
        params={
            "oid": "ZTF20aaelulu",
            "survey": "ZTF",
            "radius": "30",
            "neighbors": "10",
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()["detections"]) >= 1
    assert len(response.json()["non_detections"]) >= 1
    assert len(response.json()["forced_photometry"]) >= 1
