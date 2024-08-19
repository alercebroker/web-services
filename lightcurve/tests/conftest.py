import os
import pathlib

import psycopg2
import pytest
from db_plugins.db.mongo._connection import MongoConnection
from db_plugins.db.sql._connection import PsqlDatabase as DbpDatabase
from db_plugins.db.sql.models import (
    Detection,
    ForcedPhotometry,
    NonDetection,
    Object,
    Feature,
    FeatureVersion,
)
from fastapi.testclient import TestClient
from pymongo import MongoClient
import test_utils


@pytest.fixture(scope="session")
def docker_compose_command():
    compose_version = os.getenv("COMPOSE_VERSION", "v2")
    if compose_version == "v1":
        return "docker-compose"
    return "docker-compose"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    path = pathlib.Path(os.path.dirname(__file__)).parent / "docker-compose.yml"
    print(path)
    assert path == "."
    return path


def is_responsive_psql(url):
    try:
        conn = psycopg2.connect(
            "dbname='postgres' user='postgres' host=localhost password='postgres'"
        )
        conn.close()
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


def is_responsive_mongo(url):
    (host, port) = url.split(":")
    try:
        client = MongoClient(
            host=host,  # <-- IP and port go here
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            username="",
            password="",
            port=int(port),
        )
        client.database.somecol.insert_one({"hola": "chao"})
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

@pytest.fixture(scope="session")
def env_vars():
    os.environ["ENV"] = "test"
    os.environ["PSQL_PORT"] = "5432"
    os.environ["PSQL_HOST"] = "localhost"
    os.environ["PSQL_USER"] = "postgres"
    os.environ["PSQL_PASSWORD"] = "postgres"
    os.environ["PSQL_DATABASE"] = "postgres"
    os.environ["MONGO_PORT"] = "27017"
    os.environ["MONGO_HOST"] = "localhost"
    os.environ["MONGO_DATABASE"] = "database"
    os.environ["MONGO_USER"] = ""
    os.environ["MONGO_PASSWORD"] = ""
    os.environ["SECRET_KEY"] = "some_secret"
    yield
    os.environ.pop("MONGO_HOST")
    os.environ.pop("MONGO_PORT")
    os.environ.pop("MONGO_DATABASE")
    os.environ.pop("MONGO_USER")
    os.environ.pop("MONGO_PASSWORD")
    os.environ.pop("PSQL_PORT")
    os.environ.pop("PSQL_HOST")
    os.environ.pop("PSQL_USER")
    os.environ.pop("PSQL_PASSWORD")
    os.environ.pop("PSQL_DATABASE")
    os.environ.pop("ENV")
    os.environ.pop("SECRET_KEY")


@pytest.fixture
def init_psql(psql_service):
    user = "postgres"
    pwd = "postgres"
    host = "localhost"
    port = "5432"
    db = "postgres"
    config = {
        "USER": user,
        "PASSWORD": pwd,
        "HOST": host,
        "PORT": port,
        "DB_NAME": db,
    }
    dbp_database = DbpDatabase(config)
    dbp_database.create_db()
    yield dbp_database
    teardown_psql(dbp_database)

def teardown_psql(database):
    database.drop_db()

@pytest.fixture
def init_mongo(mongo_service):
    db = MongoConnection(
        {
            "host": "localhost",
            "username": "",
            "password": "",
            "port": 27017,
            "database": "database",
        }
    )
    db.create_db()
    yield db.client.database
    teardown_mongo(db)


def teardown_mongo(database: MongoConnection):
    database.drop_db()


@pytest.fixture
def insert_ztf_1_oid_per_aid(init_psql, init_mongo):
    """
    Only one object per aid, 1 in psql 1 in mongo.
    One detection per object.
    One non detection per object.
    One forcer photometry per object.
    """

    objects = [
        Object(**test_utils.create_object_data_psql("oid1")),
    ]
    detections = [
        Detection(**test_utils.create_detection_data_psql("oid1", 123))
    ]
    non_detections = [
        NonDetection(**test_utils.create_non_detection_data_psql("oid1"))
    ]
    forced_photometries = [
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid1", 123)
        )
    ]
    features = [
        {
            "oid": "oid1",
            "name": "SPM_chi",
            "value": None,
            "fid": 1,
            "version": "lc_classifier_1.2.1-P",
        },
        {
            "oid": "oid1",
            "name": "Multiband_period",
            "value": 296.87498481917,
            "fid": 2,
            "version": "lc_classifier_1.2.1-P",
        },
        {
            "oid": "oid1",
            "name": "PPE",
            "value": 0.042344874357211904,
            "fid": 1,
            "version": "lc_classifier_1.2.1-P",
        },
    ]
    features = [Feature(**feat) for feat in features]
    feature_versions = [FeatureVersion(version="lc_classifier_1.2.1-P")]
    with init_psql.session() as session:
        session.add_all(objects)
        session.commit()
        session.add_all(detections)
        session.add_all(non_detections)
        session.add_all(forced_photometries)
        session.add_all(feature_versions)
        session.commit()
        session.add_all(features)
        session.commit()
    init_mongo.object.insert_one(
        test_utils.create_object_data_mongo(["oid1"], "aid1")
    )
    init_mongo.detection.insert_one(
        test_utils.create_detection_data_mongo("oid1", 123, "aid1", "ztf")
    )
    init_mongo.non_detection.insert_one(
        test_utils.create_non_detection_data_mongo("oid1", "aid1", "ztf")
    )
    init_mongo.forced_photometry.insert_one(
        test_utils.create_forced_photometry_data_mongo(
            "oid1", 123, "aid1", "ztf"
        )
    )


@pytest.fixture
def insert_ztf_many_oid_per_aid(init_psql, init_mongo):
    """
    Many objects per aid, many id in psql, 1 aid in mongo.
    One detection per object
    """
    objects = [
        Object(**test_utils.create_object_data_psql("oid1")),
        Object(**test_utils.create_object_data_psql("oid2")),
        Object(**test_utils.create_object_data_psql("oid3")),
    ]
    detections = [
        Detection(**test_utils.create_detection_data_psql("oid1", 123)),
        Detection(**test_utils.create_detection_data_psql("oid2", 456)),
        Detection(**test_utils.create_detection_data_psql("oid3", 789)),
    ]
    non_detections = [
        NonDetection(**test_utils.create_non_detection_data_psql("oid1")),
        NonDetection(**test_utils.create_non_detection_data_psql("oid2")),
        NonDetection(**test_utils.create_non_detection_data_psql("oid3")),
    ]
    forced = [
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid1", 123)
        ),
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid2", 456)
        ),
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid3", 789)
        ),
    ]
    with init_psql.session() as session:
        session.add_all(objects)
        session.commit()
        session.add_all(detections)
        session.add_all(non_detections)
        session.add_all(forced)
        session.commit()

    init_mongo.object.insert_one(
        test_utils.create_object_data_mongo(["oid1", "oid2", "oid3"], "aid1")
    )
    init_mongo.detection.insert_one(
        test_utils.create_detection_data_mongo("oid1", 123, "aid1", "ztf")
    )
    init_mongo.detection.insert_one(
        test_utils.create_detection_data_mongo("oid2", 456, "aid1", "ztf")
    )
    init_mongo.detection.insert_one(
        test_utils.create_detection_data_mongo("oid3", 789, "aid1", "ztf")
    )
    init_mongo.non_detection.insert_one(
        test_utils.create_non_detection_data_mongo("oid1", "aid1", "ztf")
    )
    init_mongo.non_detection.insert_one(
        test_utils.create_non_detection_data_mongo("oid2", "aid1", "ztf")
    )
    init_mongo.non_detection.insert_one(
        test_utils.create_non_detection_data_mongo("oid3", "aid1", "ztf")
    )
    init_mongo.forced_photometry.insert_one(
        test_utils.create_forced_photometry_data_mongo(
            "oid1", 123, "aid1", "ztf"
        )
    )
    init_mongo.forced_photometry.insert_one(
        test_utils.create_forced_photometry_data_mongo(
            "oid2", 456, "aid1", "ztf"
        )
    )
    init_mongo.forced_photometry.insert_one(
        test_utils.create_forced_photometry_data_mongo(
            "oid3", 789, "aid1", "ztf"
        )
    )


@pytest.fixture
def insert_atlas_1_oid_per_aid(init_mongo, init_psql):
    """
    Only one object per aid, none in psql 1 in mongo.
    One detection per object.
    """

    init_mongo.object.insert_one(
        test_utils.create_object_data_mongo(["oid1"], "aid1")
    )
    init_mongo.detection.insert_one(
        test_utils.create_detection_data_mongo("oid1", 123, "aid1", "ATLASa01")
    )
    init_mongo.forced_photometry.insert_one(
        test_utils.create_forced_photometry_data_mongo(
            "oid1", 123, "aid1", "ATLASa01"
        )
    )


@pytest.fixture
def insert_atlas_many_oid_per_aid(init_mongo, init_psql):
    """Insert into mongodb data from ATLAS only

    Multiple oids are associated with a single aid
    """
    object = test_utils.create_object_data_mongo(["oid1", "oid2"], "aid1")
    detections = [
        test_utils.create_detection_data_mongo("oid1", 123, "aid1", "ATLAS"),
        test_utils.create_detection_data_mongo("oid2", 456, "aid1", "atlas"),
    ]
    forced = [
        test_utils.create_forced_photometry_data_mongo(
            "oid1", 123, "aid1", "atlas"
        ),
        test_utils.create_forced_photometry_data_mongo(
            "oid2", 456, "aid1", "atlas"
        ),
    ]
    init_mongo.object.insert_one(object)
    init_mongo.detection.insert_many(detections)
    init_mongo.forced_photometry.insert_many(forced)


@pytest.fixture
def insert_many_aid_ztf_and_atlas_detections(init_psql, init_mongo):
    """
    Isert 2 aids to mongo, each with 1 object from ztf and 1 from atlas.
    Will have 2 objects in psql each with 1 ztf detection
    Will have 2 objects in mongo, each witn 1 ztf detection and 1 atlas detection
    """

    objects_psql = [
        Object(**test_utils.create_object_data_psql("oid1")),
        Object(**test_utils.create_object_data_psql("oid2")),
    ]

    detections_psql = [
        Detection(**test_utils.create_detection_data_psql("oid1", 123)),
        Detection(**test_utils.create_detection_data_psql("oid2", 456)),
    ]
    non_detections_psql = [
        NonDetection(**test_utils.create_non_detection_data_psql("oid1")),
        NonDetection(**test_utils.create_non_detection_data_psql("oid2")),
    ]
    forced_psql = [
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid1", 123)
        ),
        ForcedPhotometry(
            **test_utils.create_forced_photometry_data_psql("oid2", 456)
        ),
    ]

    objects_mongo = [
        test_utils.create_object_data_mongo(["oid1", "oid3"], "aid1"),
        test_utils.create_object_data_mongo(["oid2", "oid4"], "aid2"),
    ]
    detections_mongo = [
        test_utils.create_detection_data_mongo("oid1", 123, "aid1", "ztf"),
        test_utils.create_detection_data_mongo("oid3", 789, "aid1", "atlas"),
        test_utils.create_detection_data_mongo("oid2", 456, "aid2", "ztf"),
        test_utils.create_detection_data_mongo("oid4", 987, "aid2", "atlas"),
    ]
    non_detections_mongo = [
        test_utils.create_non_detection_data_mongo("oid1", "aid1", "ztf"),
        test_utils.create_non_detection_data_mongo("oid3", "aid1", "ztf"),
    ]
    forced_mongo = [
        test_utils.create_forced_photometry_data_mongo(
            "oid1", 123, "aid1", "ztf"
        ),
        test_utils.create_forced_photometry_data_mongo(
            "oid3", 789, "aid1", "atlas"
        ),
        test_utils.create_forced_photometry_data_mongo(
            "oid2", 456, "aid2", "ztf"
        ),
        test_utils.create_forced_photometry_data_mongo(
            "oid4", 987, "aid2", "atlas"
        ),
    ]

    with init_psql.session() as session:
        session.add_all(objects_psql)
        session.commit()
        session.add_all(detections_psql)
        session.add_all(non_detections_psql)
        session.add_all(forced_psql)
        session.commit()

    init_mongo.object.insert_many(objects_mongo)
    init_mongo.detection.insert_many(detections_mongo)
    init_mongo.non_detection.insert_many(non_detections_mongo)
    init_mongo.forced_photometry.insert_many(forced_mongo)


@pytest.fixture(scope="session")
def test_client(env_vars):
    from api.api import app

    return TestClient(app)
