import pytest
import sys

sys.path.append("..")
from api.app import create_app
from api.db import db
from db_plugins.db.sql import BaseQuery, models
import json
import datetime


@pytest.fixture
def client():

    app = create_app("settings")

    with app.test_client() as client:
        with app.app_context():
            db.create_db()
            class_ = models.Class(name="Super Nova", acronym="SN")
            taxonomy = models.Taxonomy(name="Test")
            class_.taxonomies.append(taxonomy)
            classifier = models.Classifier(name="C1")
            taxonomy.classifiers.append(classifier)
            model = models.Object(
                oid="ZTF1",
                ndet=1,
                lastmjd=1.0,
                meanra=1.0,
                meandec=1.0,
                sigmara=1.0,
                sigmadec=1.0,
                deltamjd=1.0,
                firstmjd=1.0,
            )
            model.xmatches.append(models.Xmatch(catalog_id="C1", catalog_oid="O1"))
            model.magnitude_statistics.append(
                models.MagnitudeStatistics(
                    fid=1,
                    magmean=1.0,
                    magmedian=1.0,
                    magmax=1.0,
                    magmin=1.0,
                    magsigma=1.0,
                    lastmjd=1.0,
                    firstmjd=1.0,
                )
            )
            model.classifications.append(
                models.Classification(
                    class_name="Super Nova", probability=1.0, classifier_name="C1"
                )
            )

            features_object = models.FeaturesObject(
                features_version="v1", data=json.loads('{"test":"test"}')
            )
            features_object.features = models.Features(version="V1")
            model.features.append(features_object)
            model.detections.append(
                models.Detection(
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
                )
            )
            model.non_detections.append(
                models.NonDetection(
                    mjd=1, fid=1, diffmaglim=1, datetime=datetime.datetime.now()
                )
            )
            db.session.add(model)
            db.session.commit()

        yield client
        db.drop_db()
