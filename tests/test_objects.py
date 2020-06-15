import pytest
import sys

sys.path.append("..")
from api.app import create_app
from api.db import db
from api.sql import AstroObject as AstroObjectResource

from db_plugins.db.sql.models import *
from db_plugins.db.sql import BaseQuery

import json
import datetime


@pytest.fixture
def client():

    app = create_app("settings")

    with app.test_client() as client:
        with app.app_context():
            db.create_db()
            class_ = Class(name="Super Nova", acronym="SN")
            taxonomy = Taxonomy(name="Test")
            class_.taxonomies.append(taxonomy)
            classifier = Classifier(name="C1")
            taxonomy.classifiers.append(classifier)
            model = AstroObject(
                oid="ZTF1",
                nobs=1,
                lastmjd=1.0,
                meanra=1.0,
                meandec=1.0,
                sigmara=1.0,
                sigmadec=1.0,
                deltajd=1.0,
                firstmjd=1.0,
            )
            model.xmatches.append(Xmatch(catalog_id="C1", catalog_oid="O1"))
            model.magnitude_statistics = MagnitudeStatistics(
                fid=1,
                magnitude_type="psf",
                mean=1.0,
                median=1.0,
                max_mag=1.0,
                min_mag=1.0,
                sigma=1.0,
                last=1.0,
                first=1.0,
            )
            model.classifications.append(
                Classification(
                    class_name="Super Nova", probability=1.0, classifier_name="C1"
                )
            )

            features_object = FeaturesObject(data=json.loads('{"test":"test"}'))
            features_object.features = Features(version="V1")
            model.features.append(features_object)
            model.detections.append(
                Detection(
                    candid="t",
                    mjd=1,
                    fid=1,
                    ra=1,
                    dec=1,
                    rb=1,
                    magap=1,
                    magpsf=1,
                    sigmapsf=1,
                    sigmagap=1,
                    alert=json.loads('{"test":"test"}'),
                )
            )
            model.non_detections.append(
                NonDetection(
                    mjd=1, fid=1, diffmaglim=1, datetime=datetime.datetime.now()
                )
            )
            db.session.add(model)
            db.session.commit()

            def cleanup(e):
                db.session.remove()
                return e

            app.teardown_appcontext(cleanup)
        yield client
        db.drop_db()


def test_conesearch(client):
    resource = AstroObjectResource.ObjectList()
    args = {"ra": 1, "dec": 1, "radius": 0.1}
    params = resource.parse_parameters(args)
    conesearch_args = resource._parse_conesearch_args(args)
    query = resource._get_objects(params, conesearch_args)
    assert isinstance(query, BaseQuery)
    assert "q3c_radial_query(meanra, meandec,:ra, :dec, :radius)" in str(
        query.statement
    )


def test_object_list(client):
    rv = client.get("/objects/")
    assert isinstance(rv.json["results"], list)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF1"


def test_objects_list_not_found(client):
    rv = client.get("/objects/", query_string={"classifier": "Fake"})
    assert rv.status_code == 404


def test_date_query_first(client):
    obj = AstroObject(oid="ZTF2", firstmjd=2.0)
    db.session.add(obj)
    db.session.commit()
    args = {"firstmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["results"][0]["oid"] == "ZTF1"
    assert len(rv.json["results"]) == 1


def test_date_query_first_2(client):
    obj = AstroObject(oid="ZTF2", firstmjd=2.0)
    db.session.add(obj)
    db.session.commit()
    args = {"firstmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["results"][0]["oid"] == "ZTF2"
    assert len(rv.json["results"]) == 1


def test_date_query_last(client):
    obj = AstroObject(oid="ZTF2", lastmjd=2.0)
    db.session.add(obj)
    db.session.commit()
    args = {"lastmjd": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["results"][0]["oid"] == "ZTF1"
    assert len(rv.json["results"]) == 1


def test_date_query_last_2(client):
    obj = AstroObject(oid="ZTF2", lastmjd=2.0)
    db.session.add(obj)
    db.session.commit()
    args = {"lastmjd": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert rv.json["results"][0]["oid"] == "ZTF2"
    assert len(rv.json["results"]) == 1


def test_ndet_query(client):
    obj = AstroObject(oid="ZTF2", nobs=2)
    db.session.add(obj)
    db.session.commit()
    args = {"ndet": [0, 1]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF1"


def test_ndet_query_2(client):
    obj = AstroObject(oid="ZTF2", nobs=2)
    db.session.add(obj)
    db.session.commit()
    args = {"ndet": [2, 3]}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF2"


def test_classifier_query(client):
    args = {"classifier": "C1"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF1"

def test_class_query(client):
    args = {"class":"Super Nova"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF1"

def test_class_classifier_query(client):
    args = {"classifier": "C1", "class": "Super Nova"}
    rv = client.get("/objects/", query_string=args)
    assert len(rv.json["results"]) == 1
    assert rv.json["results"][0]["oid"] == "ZTF1"

def test_class_classifier_query_not_found(client):
    args = {"classifier": "C1", "class": "fake"}
    rv = client.get("/objects/", query_string=args)
    assert rv.status_code == 404
