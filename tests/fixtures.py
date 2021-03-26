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
            taxonomy = models.Taxonomy(
                classifier_name="C1", classifier_version="1.0.0-test", classes=["SN"]
            )
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
                    class_name="SN",
                    probability=1.0,
                    classifier_name=taxonomy.classifier_name,
                    classifier_version=taxonomy.classifier_version,
                    ranking=1,
                )
            )
            step_feature = models.Step(
                step_id="test_feature",
                name="feature",
                version="1",
                comments="asd",
                date=datetime.datetime.now(),
            )
            step_preprocess = models.Step(
                step_id="test_preprocess",
                name="preprocess",
                version="1",
                comments="asd",
                date=datetime.datetime.now(),
            )
            feature_version = models.FeatureVersion(
                version="1.0.0-test",
                step_id_feature=step_feature.step_id,
                step_id_preprocess=step_preprocess.step_id,
            )
            feature = models.Feature(
                oid=model.oid,
                name="testfeature",
                value=0.5,
                fid=1,
                version=feature_version.version,
            )
            model.detections.append(
                models.Detection(
                    candid=123,
                    mjd=1,
                    fid=1,
                    pid=1,
                    isdiffpos=1,
                    ra=1,
                    dec=1,
                    rb=1,
                    magpsf=1,
                    sigmapsf=1,
                    corrected=True,
                    dubious=True,
                    has_stamp=True,
                    step_id_corr=step_preprocess.step_id,
                )
            )
            model.non_detections.append(models.NonDetection(mjd=1, fid=1, diffmaglim=1))
            db.session.add(taxonomy)
            db.session.add_all([step_feature, step_preprocess])
            db.session.commit()
            db.session.add(feature_version)
            db.session.add(model)
            db.session.commit()
            db.session.close()
        yield client
        db.session.close()
        db.drop_db()
