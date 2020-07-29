import pytest
import sys

# sys.path.append("..")
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
            class_ = models.Class(fullname="Super Nova", name="SN")
            classifier = models.Classifier(name="C1", version="1.0.0-test")
            model = models.Object(
                oid="ZTF1",
                ndet=1,
                lastmjd=1.0,
                meanra=1.0,
                meandec=1.0,
                sigmara=1.0,
                sigmadec=1.0,
                deltajd=1.0,
                firstmjd=1.0,
            )
            model.magstats.append(
                models.MagStats(
                    fid=1,
                    stellar=True,
                    corrected=True,
                    ndet=1,
                    ndubious=1,
                    dmdt_first=0.13,
                    dm_first=0.12,
                    sigmadm_first=1.4,
                    dt_first=2.0,
                    magmean=19.0,
                    magmedian=20,
                    magmax=1.4,
                    magmin=1.4,
                    magsigma=1.4,
                    maglast=1.4,
                    magfirst=1.4,
                    firstmjd=1.4,
                    lastmjd=1.4,
                    step_id_corr="testing_id",
                )
            )
            model.probabilities.append(
                models.Probability(
                    class_name=class_.name,
                    probability=1.0,
                    classifier_name=classifier.name,
                    classifier_version=classifier.version,
                    ranking=1,
                )
            )
            feature_version = models.FeatureVersion(version="1.0.0-test")
            feature = models.Feature(
                oid=model.oid,
                name="testfeature",
                value=0.5,
                fid=1,
                version=feature_version.version,
            )
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
            model.non_detections.append(models.NonDetection(mjd=1, fid=1, diffmaglim=1))
            db.session.add(model)
            db.session.commit()
        yield client
        db.drop_db()
