"""Every endpoint that takes an object id accepts a ZTF object by its ZTF… name and by its numeric id.

P3-1 (lightcurve, one oid), P3-2 (lightcurve, several oids), P3-3 (list_objects and probability),
plus /object and /magstats, which accepted only one of the two formats.
"""

import pytest
from db_plugins.db.sql.models_pipeline import Detection, Object, Probability, ZtfDetection, ZtfObject
from sqlalchemy import text

from app_client import client_for as api_client
from core.idmapper.idmapper import catalog_oid_to_masterid, parse_oid

NAME = "ZTF20aaelulu"
NUMBER = str(catalog_oid_to_masterid("ZTF", NAME).item())
OTHER_NAME = "ZTF21abcdefg"
OTHER_NUMBER = str(catalog_oid_to_masterid("ZTF", OTHER_NAME).item())
N_DETECTIONS = 3


@pytest.mark.parametrize(
    "survey, oid, expected",
    [
        ("ztf", NAME, int(NUMBER)),
        ("ztf", NUMBER, int(NUMBER)),
        (None, NAME, int(NUMBER)),
        ("lsst", "170591527609303944", 170591527609303944),
        ("ztf", int(NUMBER), int(NUMBER)),
    ],
)
def test_parse_oid_accepts_both_formats(survey, oid, expected):
    assert parse_oid(survey, oid) == expected


@pytest.mark.parametrize(
    "survey, oid",
    [("ztf", "ZTF20AAELULU"), ("ztf", "abc"), ("lsst", NAME), ("lsst", "abc"), ("foo", NUMBER), (None, "abc")],
)
def test_parse_oid_rejects_anything_else(survey, oid):
    with pytest.raises(ValueError):
        parse_oid(survey, oid)


@pytest.mark.parametrize("survey", [None, "ztf"])
@pytest.mark.parametrize("oid", [NAME.lower(), NAME.upper(), "Ztf20aaelulu"])
def test_a_ztf_name_wrong_only_in_case_is_rejected_with_a_suggestion(survey, oid):
    with pytest.raises(ValueError, match=rf"^Invalid ZTF object ID: {oid}\. Did you mean {NAME}\?$"):
        parse_oid(survey, oid)


@pytest.mark.parametrize("survey, oid", [(None, "ztf20aaelul"), ("ztf", "ZTF2aaaelulu"), ("ztf", "ZTF20aaelul1")])
def test_a_ztf_name_wrong_in_other_ways_gets_the_format(survey, oid):
    with pytest.raises(ValueError, match=r"Expected ZTF, two digits and seven lowercase letters, for example"):
        parse_oid(survey, oid)


@pytest.fixture
def ztf_objects(db):
    objects = [
        Object(oid=int(number), tid=0, sid=0, meanra=10.0, meandec=10.0, firstmjd=60000, lastmjd=60010)
        for number in (NUMBER, OTHER_NUMBER)
    ]
    with db.session() as session:
        session.add_all(objects)
        session.commit()
        for number in (NUMBER, OTHER_NUMBER):
            session.add(ZtfObject(oid=int(number), stellar=False, corrected=False))
            session.add(
                Probability(
                    oid=int(number),
                    sid=0,
                    classifier_id=2,
                    classifier_version=1,
                    class_id=3,
                    probability=0.5,
                    ranking=1,
                    lastmjd=60010,
                )
            )
            for i in range(N_DETECTIONS):
                session.add(
                    Detection(oid=int(number), sid=0, measurement_id=i, mjd=60000 + i, ra=10.0, dec=10.0, band=1)
                )
                session.add(ZtfDetection(oid=int(number), measurement_id=i, magpsf=18.0, sigmapsf=0.1))
        session.commit()
    yield db
    with db.session() as session:
        session.execute(text("DELETE FROM probability"))
        session.execute(text("DELETE FROM ztf_object"))
        session.commit()


def client_for(api, db):
    return api_client(api, db, raise_server_exceptions=False)


@pytest.mark.parametrize("oid", [NAME, NUMBER])
def test_lightcurve_single_oid(ztf_objects, oid):
    response = client_for("lightcurve_api", ztf_objects).get("/detections", params={"survey_id": "ztf", "oid": [oid]})

    assert response.status_code == 200
    assert len(response.json()) == N_DETECTIONS


@pytest.mark.parametrize("oids", [[NAME, OTHER_NAME], [NUMBER, OTHER_NAME], [NUMBER, OTHER_NUMBER]])
def test_lightcurve_several_oids(ztf_objects, oids):
    response = client_for("lightcurve_api", ztf_objects).get("/detections", params={"survey_id": "ztf", "oid": oids})

    assert response.status_code == 200
    assert len(response.json()) == 2 * N_DETECTIONS


@pytest.mark.parametrize("oid", [NAME, NUMBER])
def test_list_objects_by_oid(ztf_objects, oid):
    response = client_for("object_api", ztf_objects).get("/list_objects", params={"survey": "ztf", "oid": [oid]})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


@pytest.mark.parametrize("oid", [NAME, NUMBER])
def test_object(ztf_objects, oid):
    response = client_for("object_api", ztf_objects).get("/object", params={"survey_id": "ztf", "oid": oid})

    assert response.status_code == 200


@pytest.mark.parametrize(
    "params", [{"oid": NAME}, {"oid": NUMBER, "survey_id": "ztf"}, {"oid": NAME, "survey_id": "ztf"}]
)
def test_probability(ztf_objects, params):
    response = client_for("probability_api", ztf_objects).get("/probability", params=params)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_probability_suggests_the_right_spelling_for_a_lowercase_ztf_name(ztf_objects):
    response = client_for("probability_api", ztf_objects).get("/probability", params={"oid": NAME.lower()})

    assert response.status_code == 400
    assert response.json()["detail"] == f"Invalid ZTF object ID: {NAME.lower()}. Did you mean {NAME}?"


@pytest.mark.parametrize(
    "api, path, params",
    [
        ("lightcurve_api", "/detections", {"survey_id": "ztf", "oid": ["abc"]}),
        ("lightcurve_api", "/detections", {"survey_id": "ztf", "oid": ["abc", NAME]}),
        ("object_api", "/list_objects", {"survey": "ztf", "oid": ["abc"]}),
        ("object_api", "/object", {"survey_id": "ztf", "oid": "abc"}),
        ("probability_api", "/probability", {"oid": "abc"}),
        ("magstat_api", "/magstats", {"survey_id": "ztf", "oid": "abc"}),
    ],
)
def test_bad_oid_is_400(ztf_objects, api, path, params):
    assert client_for(api, ztf_objects).get(path, params=params).status_code == 400


def test_magstats_takes_the_numeric_id(ztf_objects):
    # No magstats rows here: the point is that the number is looked up (404), not refused (400)
    response = client_for("magstat_api", ztf_objects).get("/magstats", params={"survey_id": "ztf", "oid": NUMBER})

    assert response.status_code == 404
