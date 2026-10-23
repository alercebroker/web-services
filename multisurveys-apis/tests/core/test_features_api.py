"""NEW-1: the features API (the client's query_features / query_feature) and classifier /classes (query_classes)."""

import pytest
from db_plugins.db.sql.models_pipeline import Feature, FeatureNameLut, FeatureVersionLut, Object
from sqlalchemy import text

from app_client import client_for
from core.idmapper.idmapper import catalog_oid_to_masterid

NAME = "ZTF20aaelulu"
NUMBER = catalog_oid_to_masterid("ZTF", NAME).item()
ZTF = 0
# The test database is created with LSST feature names only (sid=1), so the ZTF ones are added here
ZTF_FEATURES = {0: "Amplitude", 1: "Mean"}
VERSION_ID, VERSION_NAME = 1, "27.5.6"


@pytest.fixture
def client(db):
    with db.session() as session:
        session.add(Object(oid=NUMBER, tid=0, sid=ZTF, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010))
        session.add_all(FeatureNameLut(feature_id=i, feature_name=n, sid=ZTF, tid=0) for i, n in ZTF_FEATURES.items())
        session.add(FeatureVersionLut(version_id=VERSION_ID, version_name=VERSION_NAME, sid=ZTF, tid=0))
        session.commit()
        session.add_all(
            Feature(
                oid=NUMBER, sid=ZTF, feature_id=feature_id, band=band, version=VERSION_ID, value=feature_id + band / 10
            )
            for feature_id in ZTF_FEATURES
            for band in (1, 2)
        )
        session.commit()

    def _client(api):
        return client_for(api, db, raise_server_exceptions=False)

    yield _client

    with db.session() as session:
        session.execute(text("DELETE FROM feature"))
        session.execute(text(f"DELETE FROM feature_name_lut WHERE sid = {ZTF}"))
        session.execute(text(f"DELETE FROM feature_version_lut WHERE sid = {ZTF}"))
        session.commit()


@pytest.mark.parametrize("oid", [NAME, str(NUMBER)])
def test_all_features_of_an_object(client, oid):
    response = client("features_api").get("/features", params={"oid": oid, "survey_id": "ztf"})

    assert response.status_code == 200
    assert response.json() == [
        {"name": "Amplitude", "value": 0.1, "band": 1, "version": VERSION_NAME},
        {"name": "Amplitude", "value": 0.2, "band": 2, "version": VERSION_NAME},
        {"name": "Mean", "value": 1.1, "band": 1, "version": VERSION_NAME},
        {"name": "Mean", "value": 1.2, "band": 2, "version": VERSION_NAME},
    ]


@pytest.mark.parametrize(
    "params, expected",
    [
        ({"name": "Mean"}, [("Mean", 1), ("Mean", 2)]),
        ({"band": 2}, [("Amplitude", 2), ("Mean", 2)]),
        ({"name": "Mean", "band": 1}, [("Mean", 1)]),
        ({"version": VERSION_NAME}, [("Amplitude", 1), ("Amplitude", 2), ("Mean", 1), ("Mean", 2)]),
        ({"version": "0.0.0"}, []),
        ({"name": "NoSuchFeature"}, []),
    ],
)
def test_feature_filters(client, params, expected):
    response = client("features_api").get("/features", params={"oid": NAME, "survey_id": "ztf", **params})

    assert response.status_code == 200
    assert [(f["name"], f["band"]) for f in response.json()] == expected


@pytest.mark.parametrize(
    "params, status",
    [
        ({"oid": "ZTF99zzzzzzz", "survey_id": "ztf"}, 404),
        ({"oid": "abc", "survey_id": "ztf"}, 400),
        ({"oid": NAME, "survey_id": "foo"}, 400),
    ],
)
def test_features_errors(client, params, status):
    assert client("features_api").get("/features", params=params).status_code == status


def test_classes_of_a_classifier_version(client):
    # Seeded by the test database: stamp_classifier_2025_beta 2.1.1 with SN, AGN, VS, asteroid, bogus, satellite
    response = client("classifier_api").get(
        "/classes", params={"classifier_name": "stamp_classifier_2025_beta", "classifier_version": "2.1.1"}
    )

    assert response.status_code == 200
    assert response.json() == [{"name": n} for n in ("SN", "AGN", "VS", "asteroid", "bogus", "satellite")]


@pytest.mark.parametrize("name, version", [("stamp_classifier_2025_beta", "9.9.9"), ("foo", "2.1.1")])
def test_classes_of_an_unknown_classifier_is_404(client, name, version):
    response = client("classifier_api").get("/classes", params={"classifier_name": name, "classifier_version": version})

    assert response.status_code == 404
