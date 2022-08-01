from api.resources.astro_object import astro_object as AstroObjectResource
from conftest import models


def test_conesearch(client):
    resource = AstroObjectResource.ObjectList()
    args = {"ra": 1, "dec": 1, "radius": 0.1}
    params = resource._convert_conesearch_args(args)
    statement = resource._create_conesearch_statement(params)
    assert "q3c_radial_query(meanra, meandec,:ra, :dec, :radius)" in str(
        statement
    )


def test_order_by_desc(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    db.session.close()
    args = {"order_by": "firstmjd", "order_mode": "DESC"}
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["oid"] == "ZTF2"


def test_order_by_asc(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"order_by": "firstmjd", "order_mode": "ASC"}
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["oid"] == "ZTF1"


def test_order_by_class_attribute_desc(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    obj.probabilities.append(
        models.Probability(
            class_name="SN",
            probability=0.5,
            classifier_name="C1",
            classifier_version="1.0.0-test",
            ranking=1,
        )
    )
    db.session.add(obj)
    db.session.commit()
    args = {
        "classifier": "C1",
        "classifier_version": "1.0.0-test",
        "order_by": "probability",
        "order_mode": "DESC",
    }
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["oid"] == "ZTF1"


def test_order_by_class_attribute_asc(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    obj.probabilities.append(
        models.Probability(
            class_name="VS",
            probability=0.5,
            classifier_name="C1",
            classifier_version="1.0.0-test",
            ranking=1,
        )
    )
    db.session.add(obj)
    db.session.commit()
    args = {
        "classifier": "C1",
        "classifier_version": "1.0.0-test",
        "order_by": "probability",
        "order_mode": "ASC",
    }
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["oid"] == "ZTF2"


def test_object_list(client):
    rv = client.get("/objects/")
    assert isinstance(rv.json["items"], list)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


def test_objects_list_not_found(client):
    rv = client.get(
        "/objects/", query_string={"classifier": "Fake", "count": "true"}
    )
    assert rv.json["total"] == 0


def test_date_query_first(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"firstmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["oid"] == "ZTF1"
    assert len(rv.json["items"]) == 1


def test_date_query_first_2(client, app):
    obj = models.Object(oid="ZTF2", firstmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"firstmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["oid"] == "ZTF2"
    assert len(rv.json["items"]) == 1


def test_date_query_last(client, app):
    obj = models.Object(oid="ZTF2", lastmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"lastmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["oid"] == "ZTF1"
    assert len(rv.json["items"]) == 1


def test_date_query_last_2(client, app):
    obj = models.Object(oid="ZTF2", lastmjd=2.0)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"lastmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["oid"] == "ZTF2"
    assert len(rv.json["items"]) == 1


def test_ndet_query(client, app):
    obj = models.Object(oid="ZTF2", ndet=2)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"ndet": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


def test_ndet_query_2(client, app):
    obj = models.Object(oid="ZTF2", ndet=2)
    db = app.container.psql_db()
    db.session.add(obj)
    db.session.commit()
    args = {"ndet": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF2"


def test_classifier_query(client):
    args = {"classifier": "C1"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


def test_class_query(client):
    args = {"class": "SN"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


def test_class_classifier_query(client):
    args = {"classifier": "C1", "class": "SN"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


def test_class_classifier_query_not_found(client):
    args = {"classifier": "C1", "class": "fake"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 0


def test_single_object_query(client):
    rv = client.get("/objects/ZTF1")
    assert rv.status_code == 200
    assert rv.json["oid"] == "ZTF1"
