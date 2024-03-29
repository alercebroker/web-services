import pytest
import sys
import pathlib
import os
import psycopg2
import pymongo
from db_plugins.db.sql import models
from db_plugins.db.sql.connection import SQLConnection
from db_plugins.db.mongo import models as mongo_models
import datetime

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve() / "src/"))


@pytest.fixture(scope="session")
def docker_compose_command():
    compose_version = os.getenv("COMPOSE_VERSION", "v1")
    if compose_version == "v1":
        return "docker-compose"
    return "docker compose"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "tests", "docker-compose.yml"
    )


def is_responsive_psql(url):
    try:
        conn = psycopg2.connect(
            "dbname='postgres' user='postgres' host=localhost password='postgres'"
        )
        conn.close()
        return True
    except Exception:
        return False


def is_responsive_mongo(url):
    (host, port) = url.split(":")
    try:
        client = pymongo.MongoClient(
            host=host,  # <-- IP and port go here
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            username="mongo",
            password="mongo",
            port=int(port),
            authSource="database",
        )
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def psql_service(docker_ip, docker_services):
    """Ensure that Kafka service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("postgres", 5432)
    server = "{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive_psql(server)
    )
    return server


@pytest.fixture(scope="session")
def mongo_service(docker_ip, docker_services):
    """Ensure that Kafka service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("mongo", 27017)
    server = "{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive_mongo(server)
    )
    return server


@pytest.fixture
def app(psql_service, mongo_service):
    from api.app import create_app

    app = create_app("./tests/config.yml")
    yield app
    app.container.unwire()


@pytest.fixture
def populate_databases(app):
    with app.app_context():
        db = SQLConnection()
        psql_config = app.container.database_config.SQL()
        SQLALCHEMY_DATABASE_URL = f"postgresql://{psql_config['USER']}:{psql_config['PASSWORD']}@{psql_config['HOST']}:{psql_config['PORT']}/{psql_config['DATABASE']}"
        psql_config["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
        db.connect(psql_config)
        mongo_db = app.container.mongo_db().mongo_db
        db.create_db()
        mongo_db.create_db()

        # psql data
        taxonomy = models.Taxonomy(
            classifier_name="C1",
            classifier_version="1.0.0-test",
            classes=["SN"],
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
        model.features.append(feature)
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
        model.non_detections.append(
            models.NonDetection(mjd=1, fid=1, diffmaglim=1)
        )
        db.session.add(taxonomy)
        db.session.add_all([step_feature, step_preprocess])
        db.session.commit()
        db.session.add(feature_version)
        db.session.add(model)
        db.session.commit()
        db.session.close()

        # mongo data
        mongo_object = mongo_models.Object(
            aid="AID_ATLAS1",
            tid=["ATLAS"],
            sid=["ATLAS"],
            oid=["ATLAS1"],
            lastmjd="lastmjd",
            firstmjd="firstmjd",
            meanra=100.0,
            meandec=50.0,
            sigmara=0.1,
            sigmadec=0.1,
            ndet="ndet",
            corrected=False,
            stellar=False,
        )
        mongo_object_2 = mongo_models.Object(
            aid="AID_ATLAS2",
            oid=["ATLAS2", "ZTF2"],
            tid=["ATLAS", "ZTF"],
            sid=["ATLAS", "ZTF"],
            lastmjd="lastmjd",
            firstmjd="firstmjd",
            meanra=100.0,
            meandec=50.0,
            sigmara=0.1,
            sigmadec=0.1,
            ndet="ndet",
            corrected=False,
            stellar=False,
        )
        mongo_detections = mongo_models.Detection(
            tid="ATLAS01",
            sid="ATLAS",
            aid="AID_ATLAS1",
            oid=["ATLAS1"],
            candid="candid1",
            mjd=1,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            mag_corr=1,
            e_mag=1,
            e_mag_corr=1,
            e_mag_corr_ext=1,
            rfid=1,
            e_ra=1,
            e_dec=1,
            isdiffpos=1,
            magpsf_corr=1,
            sigmapsf_corr=1,
            sigmapsf_corr_ext=1,
            corrected=True,
            dubious=True,
            parent_candid=1234,
            has_stamp=True,
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
        mongo_detections_2 = mongo_models.Detection(
            tid="ATLAS02",
            sid="ATLAS",
            aid="AID_ATLAS2",
            oid=["ATLAS2", "ZTF2"],
            candid="candid2",
            mjd=1,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            mag_corr=1,
            e_mag=1,
            e_mag_corr=1,
            e_mag_corr_ext=1,
            rfid=1,
            e_ra=1,
            e_dec=1,
            isdiffpos=1,
            magpsf_corr=1,
            sigmapsf_corr=1,
            sigmapsf_corr_ext=1,
            corrected=True,
            dubious=True,
            parent_candid=float("nan"),
            has_stamp=True,
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
        moongo_non_detections = mongo_models.NonDetection(
            candid="candid",
            aid="AID_ATLAS1",
            oid="ATLAS1",
            tid="ATLAS01",
            sid="ATLAS",
            mjd=1,
            diffmaglim=1,
            fid=1,
        )
        mongo_db.query().get_or_create(mongo_object, model=mongo_models.Object)
        mongo_db.query().get_or_create(
            mongo_object_2, model=mongo_models.Object
        )
        mongo_db.query().get_or_create(
            mongo_detections, model=mongo_models.Detection
        )
        mongo_db.query().get_or_create(
            mongo_detections_2, model=mongo_models.Detection
        )
        mongo_db.query().get_or_create(
            moongo_non_detections, model=mongo_models.NonDetection
        )

    yield app
    db.session.close()
    db.drop_db()
    mongo_db.drop_db()


@pytest.fixture
def client(populate_databases):
    app = populate_databases
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    db = SQLConnection()
    psql_config = app.container.database_config.SQL()
    SQLALCHEMY_DATABASE_URL = f"postgresql://{psql_config['USER']}:{psql_config['PASSWORD']}@{psql_config['HOST']}:{psql_config['PORT']}/{psql_config['DATABASE']}"
    psql_config["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
    db.connect(psql_config)
    yield db
