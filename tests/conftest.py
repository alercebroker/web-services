import pytest
import sys
import pathlib
import os
import pymongo
from db_plugins.db.mongo import models

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve() / "src/"))


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "tests", "docker-compose.yml"
    )


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
def app(mongo_service):
    from api.app import create_app

    app = create_app("./tests/config.yml")
    yield app
    app.container.unwire()


@pytest.fixture
def populate_databases(app):
    with app.app_context():
        db = app.container.mongo_db()
        db.create_db()

        # mongo data
        object = models.Object(
            _id="AID_ATLAS1",
            aid="AID_ATLAS1",
            oid=["ATLAS1"],
            tid=["ATLAS"],
            corrected=False,
            stellar=False,
            lastmjd=99.,
            firstmjd=99.,
            meanra=100.0,
            sigmara=0.1,
            meandec=50.0,
            sigmadec=0.1,
            ndet=10,
        )
        object_2 = models.Object(
            _id="AID_ATLAS2",
            aid="AID_ATLAS2",
            oid=["ATLAS2", "ZTF2"],
            tid=["ATLAS", "ZTF"],
            corrected=False,
            stellar=False,
            lastmjd=99.,
            firstmjd=99.,
            meanra=100.0,
            sigmara=0.1,
            meandec=50.0,
            sigmadec=0.1,
            ndet=10,
        )
        object_3 = models.Object(
            _id="ALERCE1",
            aid="ALERCE1",
            oid=["ZTF1"],
            tid=["ZTF"],
            corrected=False,
            stellar=False,
            ndet=1,
            lastmjd=1.0,
            meanra=1.0,
            sigmara=0.1,
            meandec=1.0,
            sigmadec=0.1,
            firstmjd=1.0,
            probabilities=[dict(
                class_name="SN",
                probability=1.0,
                classifier_name="C1",
                classifier_version="1.0.0-test",
                ranking=1,
            )]
        )
        detections = models.Detection(
            tid="ATLAS01",
            aid="AID_ATLAS1",
            oid="ATLAS1",
            candid="candid1",
            mjd=1,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            e_mag=1,
            mag_corr=2,
            e_mag_corr=2,
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
            parent_candidate=None
        )
        detections_2 = models.Detection(
            tid="ZTF02",
            aid="AID_ZTF2",
            oid="ZTF2",
            candid="candid2",
            mjd=1,
            fid=1,
            ra=1,
            dec=1,
            rb=1,
            mag=1,
            e_mag=1,
            mag_corr=2,
            e_mag_corr=2,
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
            parent_candidate=None
        )
        non_detections = models.NonDetection(
            candid="candid3",
            aid="AID_ATLAS1",
            oid="ATLAS1",
            tid="ATLAS01",
            mjd=1,
            diffmaglim=1,
            fid=1,
        )
        non_detections2 = models.NonDetection(
            candid="candid4",
            aid="AID_ZTF2",
            oid="ZTF2",
            tid="ZTF02",
            mjd=1,
            diffmaglim=1,
            fid=1,
        )
        taxonomy = models.Taxonomy(
            classifier_name="C1",
            classifier_version="1.0.0-test",
            classes=["SN"],
        )
        db.query().get_or_create(taxonomy, model=models.Taxonomy)
        db.query().get_or_create(object, model=models.Object)
        db.query().get_or_create(
            object_2, model=models.Object
        )
        db.query().get_or_create(
            object_3, model=models.Object
        )
        db.query().get_or_create(
            detections, model=models.Detection
        )
        db.query().get_or_create(
            detections_2, model=models.Detection
        )
        db.query().get_or_create(
            non_detections, model=models.NonDetection
        )
        db.query().get_or_create(
            non_detections2, model=models.NonDetection
        )

    yield app
    db.drop_db()


@pytest.fixture
def client(populate_databases):
    app = populate_databases
    with app.test_client() as client:
        yield client
