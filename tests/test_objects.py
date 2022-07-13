import unittest
from conftest import mongo_models


def test_order_by_desc(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"oid": ["ZTF1"], "order_by": "firstmjd", "order_mode": "DESC"}
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["aid"] == "ALERCE2"


def test_order_by_asc(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"oid": ["ZTF1"], "order_by": "firstmjd", "order_mode": "ASC"}
    r = client.get("/objects/", query_string=args)
    assert len(r.json["items"]) == 2
    assert r.json["items"][0]["aid"] == "ALERCE1"


@unittest.skip("Classifier not implemented in mongo")
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


@unittest.skip("Classifier not implemented in mongo")
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
    assert len(rv.json["items"]) == 3


def test_object_pagination(client):
    rv = client.get("/objects/", query_string={"count": "true", "page_size": 2})
    assert len(rv.json["items"]) == 2
    assert rv.json["total"] == 3


def test_objects_list_not_found(client):
    rv = client.get(
        "/objects/", query_string={"oid": "fake", "count": "true"}
    )
    assert len(rv.json["items"]) == 0
    assert rv.json["total"] == 0


def test_date_query_first(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"firstmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["aid"] == "ALERCE1"
    assert len(rv.json["items"]) == 1


def test_conesearch_success(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=50.0,
        meandec=45.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {'ra': 50, 'dec': 45, 'radius': 30}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["aid"] == "ALERCE2"


def test_conesearch_failure(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=50.0,
        meandec=45.6,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {'ra': 50, 'dec': 45, 'radius': 30}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 0


def test_date_query_first_2(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"firstmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["aid"] == "ALERCE2"
    assert len(rv.json["items"]) == 1


def test_date_query_last(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"lastmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["aid"] == "ALERCE1"
    assert len(rv.json["items"]) == 1


def test_date_query_last_2(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"lastmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["items"][0]["aid"] == "ALERCE2"
    assert len(rv.json["items"]) == 1


def test_ndet_query(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"ndet": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["aid"] == "ALERCE1"


def test_ndet_query_2(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=2.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    args = {"ndet": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["aid"] == "ALERCE2"


@unittest.skip("Classifier not implemented in mongo")
def test_classifier_query(client):
    args = {"classifier": "C1"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


@unittest.skip("Classifier not implemented in mongo")
def test_class_query(client):
    args = {"class": "SN"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


@unittest.skip("Classifier not implemented in mongo")
def test_class_classifier_query(client):
    args = {"classifier": "C1", "class": "SN"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 1
    assert rv.json["items"][0]["oid"] == "ZTF1"


@unittest.skip("Classifier not implemented in mongo")
def test_class_classifier_query_not_found(client):
    args = {"classifier": "C1", "class": "fake"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["items"]) == 0


def test_single_object_query(client):
    rv = client.get("/objects/ALERCE1")
    assert rv.status_code == 200
    assert rv.json["aid"] == "ALERCE1"


def test_limit_values(client, app):
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=-1.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=-1
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    obj = mongo_models.Object(
        aid="ALERCE2",
        oid=["ZTF1"],
        firstmjd=1000.0,
        lastmjd=2.0,
        meanra=100.0,
        meandec=50.0,
        ndet=1000
    )
    app.container.mongo_db().query().get_or_create(obj, model=mongo_models.Object)
    rv = client.get("/objects/limit_values")
    assert rv.status_code == 200
    assert rv.json["min_ndet"] == -1
    assert rv.json["max_ndet"] == 1000
    assert rv.json["min_firstmjd"] == -1
    assert rv.json["max_firstmjd"] == 1000
