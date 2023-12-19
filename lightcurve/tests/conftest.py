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
)
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.database import Database
from utils import *


@pytest.fixture(scope="session")
def docker_compose_command():
    compose_version = os.getenv("COMPOSE_VERSION", "v1")
    if compose_version == "v1":
        return "docker-compose"
    return "docker compose"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    try:
        path = pathlib.Path(pytestconfig.rootdir) / "tests/docker-compose.yml"
        assert path.exists()
        return path
    except AssertionError:
        path = (
            pathlib.Path(pytestconfig.rootdir)
            / "lightcurve/tests/docker-compose.yml"
        )
        assert path.exists()
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
            username="mongo",
            password="mongo",
            port=int(port),
            authSource="database",
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


@pytest.fixture
def init_psql():
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
    yield dbp_database
    teardown_psql(dbp_database)


@pytest.fixture
def psql_session():
    os.environ["PSQL_PORT"] = "5432"
    os.environ["PSQL_HOST"] = "localhost"
    os.environ["PSQL_USER"] = "postgres"
    os.environ["PSQL_PASSWORD"] = "postgres"
    os.environ["PSQL_DATABASE"] = "postgres"
    from database.sql import session

    return session


@pytest.fixture(scope="session")
def mongo_database():
    os.environ["MONGO_PORT"] = "27017"
    os.environ["MONGO_HOST"] = "localhost"
    os.environ["MONGO_USER"] = "mongo"
    os.environ["MONGO_PASSWORD"] = "mongo"
    os.environ["MONGO_DATABASE"] = "database"
    os.environ["MONGO_AUTH_SOURCE"] = "admin"
    os.environ["SECRET_KEY"] = "some_secret"
    from database.mongo import database

    return database


# caso1: solo ZTF 1 oid por aid
# caso2: solo ZTF >1 oid por aid
# caso3: solo ATLAS 1 oid por aid
# caso4: solo ATLAS >1 oid por aid
# caso5: ZTF y ATLAS en un mismo aid

# PSQL - oid1
# PSQL - oid2
# Mongo - AID1 -> oid1, oid2, atlas1, atlas2

# query(oid1, survey_id=ztf) -> oid1, oid2
# query(oid1, survey_id=atlas) -> atlas1, atlas2
# query(oid1) -> oid1, oid2, atlas1, atlas2

@pytest.fixture
def insert_ztf_1_oid_per_aid(session, mongodb):
    """
    Only one object per aid, 1 in psql 1 in mongo.
    One detection per object.
    One non detection per object.
    One forcer photometry per object.
    """
    
    objects = [
        Object(**create_object_data_psql("oid1")),
    ]
    detections = [
        Detection(**create_detection_data_psql("oid1", 123))
    ]
    non_detections = [
        Detection(**create_non_detection_data_psql("oid1"))
    ]
    forced_photometries = [ForcedPhotometry(**create_forced_photometry_data_psql("oid1"))]
    session.add_all(objects)
    session.add_all(detections)
    session.add_all(non_detections)
    session.add_all(forced_photometries)
    session.commit()
    mongodb.object.insert_one(create_object_data_mongo(["oid1"], "aid1"))
    mongodb.detection.insert_one(create_detection_data_mongo("oid1", 123, "aid1", "ztf"))
    mongodb.non_detection.insert_one(create_non_detection_data_mongo("oid1", "aid1", "atlas"))
    mongodb.forced_photometry.insert_one(create_forced_photometry_data_mongo("oid1", 123, "aid1", "ztf"))

@pytest.fixture
def insert_ztf_many_oid_per_aid(session, mongodb):
    """
    Many objects per aid, many id in psql, 1 aid in mongo.
    One detection per object
    """

    objects = [
        Object(**create_object_data_psql("oid1")),
        Object(**create_object_data_psql("oid2")),
        Object(**create_object_data_psql("oid3")),
    ]
    detections = [
        Detection(**create_detection_data_psql("oid1", 123)),
        Detection(**create_detection_data_psql("oid2", 456)),
        Detection(**create_detection_data_psql("oid3", 789)),
    ]
    non_detections = [
        NonDetection(**create_non_detection_data_mongo("oid1", "aid1")),
        NonDetection(**create_non_detection_data_mongo("oid2", "aid1")),
        NonDetection(**create_non_detection_data_mongo("oid3", "aid1"))
    ]
    forced = [
        ForcedPhotometry(**create_forced_photometry_data_psql("oid1")),
        ForcedPhotometry(**create_forced_photometry_data_psql("oid2")),
        ForcedPhotometry(**create_forced_photometry_data_psql("oid3")),
    ]
    session.add_all(objects)
    session.add_all(detections)
    session.add_all(non_detections)
    session.add_all(forced)
    session.commit()
    
    mongodb.object.insert_one(create_object_data_mongo(["oid1","oid2", "oid3"], "aid1"))
    mongodb.detection.insert_one(create_detection_data_mongo("oid1", 123, "aid1", "ztf"))
    mongodb.detection.insert_one(create_detection_data_mongo("oid2", 456, "aid1", "ztf"))
    mongodb.detection.insert_one(create_detection_data_mongo("oid3", 789, "aid1", "ztf"))
    mongodb.detection.insert_one(create_non_detection_data_mongo("oid1", "aid1", "ztf"))
    mongodb.detection.insert_one(create_non_detection_data_mongo("oid2", "aid1", "ztf"))
    mongodb.detection.insert_one(create_non_detection_data_mongo("oid3", "aid1", "ztf"))
    mongodb.detection.insert_one(create_forced_photometry_data_mongo("oid1", 123, "aid1", "ztf"))
    mongodb.detection.insert_one(create_forced_photometry_data_mongo("oid2", 456, "aid1", "ztf"))
    mongodb.detection.insert_one(create_forced_photometry_data_mongo("oid3", 789, "aid1", "ztf"))

@pytest.fixture
def insert_atlas_1_oid_per_aid(mongodb):
    """
    Only one object per aid, none in psql 1 in mongo.
    One detection per object.
    """
    
    mongodb.object.insert_one(create_object_data_mongo(["oid1"], "aid1"))
    mongodb.detection.insert_one(create_detection_data_mongo("oid1", 123, "aid1", "ATLASa01"))
    mongodb.forced_photometr.insert_one(create_forced_photometry_data_mongo("oid1", 123, "aid1", "ATLASa01"))

@pytest.fixture
def insert_atlas_many_oid_per_aid(mongodb):
    """Insert into mongodb data from ATLAS only

    Multiple oids are associated with a single aid
    """
    object = create_object_data_mongo(["oid1", "oid2"], "aid1")
    detections = [create_detection_data_mongo("oid1", 123, "aid1", "ATLAS"), create_detection_data_mongo("oid2", 456, "aid1", "atlas")]
    forced = [create_forced_photometry_data_mongo("oid1", 123, "aid1", "atlas"), create_forced_photometry_data_mongo("oid2", 456, "aid1", "atlas")]
    mongodb.object.insert_one(object)
    mongodb.detection.insert_many(detections)
    mongodb.detection.insert_many(forced)

@pytest.fixture
def insert_many_aid_ztf_and_atlas_detections(session, mongodb):
    """
    Isert 2 aids to mongo, each with 1 object from ztf and 1 from atlas.
    Will have 2 objects in psql each with 1 ztf detection
    Will have 2 objects in mongo, each witn 1 ztf detection and 1 atlas detection
    """

    objects_psql = [
        Object(**create_object_data_psql("oid1")),
        Object(**create_object_data_psql("oid2")),
    ]

    detections_psql = [
        Detection(**create_detection_data_psql("oid1", 123)),
        Detection(**create_detection_data_psql("oid2", 456)),
    ]
    non_detections_psql = [
        NonDetection(**create_non_detection_data_psql("oid1")),
        NonDetection(**create_non_detection_data_psql("oid2")),
    ]
    forced_psql = [
        ForcedPhotometry(**create_forced_photometry_data_psql("oid1")),
        ForcedPhotometry(**create_forced_photometry_data_psql("oid2")),
    ]

    objects_mongo = [
        create_object_data_mongo(["oid1, oid3"], "aid1"),
        create_object_data_mongo(["oid2, oid4"], "aid2"),
    ]
    detections_mongo = [
        create_detection_data_mongo("oid1", 123, "aid1", "ztf"),
        create_detection_data_mongo("oid3", 789, "aid1", "atlas"),
        create_detection_data_mongo("oid2", 456, "aid2", "ztf"),
        create_detection_data_mongo("oid4", 987, "aid2", "atlas"),
    ]
    non_detections_mongo = [
        create_non_detection_data_mongo("oid1", "aid1", "ztf"),
        create_non_detection_data_mongo("oid3", "aid1", "atlas"),
        create_non_detection_data_mongo("oid2", "aid2", "ztf"),
        create_non_detection_data_mongo("oid4", "aid2", "atlas"),
    ]
    forced_mongo = [
        create_forced_photometry_data_mongo("oid1", 123, "aid1", "ztf"),
        create_forced_photometry_data_mongo("oid3", 789, "aid1", "atlas"),
        create_forced_photometry_data_mongo("oid2", 456, "aid2", "ztf"),
        create_forced_photometry_data_mongo("oid4", 987, "aid2", "atlas"),
    ]

    session.add_all(objects_psql)
    session.add_all(detections_psql)
    session.add_all(non_detections_psql)
    session.add_all(forced_psql)
    session.commit()
    
    mongodb.object.insert_many(objects_mongo)
    mongodb.detection.insert_many(detections_mongo)
    mongodb.non_detection.insert_many(non_detections_mongo)
    mongodb.forced_photometr.insert_many(forced_mongo)


def teardown_psql(database):
    database.drop_db()


@pytest.fixture
def init_mongo():
    db = MongoConnection(
        {
            "host": "localhost",
            "serverSelectionTimeoutMS": 3000,  # 3 second timeout
            "username": "mongo",
            "password": "mongo",
            "port": 27017,
            "database": "database",
        }
    )
    yield db.client.database
    teardown_mongo(db)

def teardown_mongo(database: MongoConnection):
    database.drop_db()


@pytest.fixture(scope="session")
def test_client():
    os.environ["ENV"] = "test"
    os.environ["PSQL_PORT"] = "5432"
    os.environ["PSQL_HOST"] = "localhost"
    os.environ["PSQL_USER"] = "postgres"
    os.environ["PSQL_PASSWORD"] = "postgres"
    os.environ["PSQL_DATABASE"] = "postgres"
    os.environ["MONGO_PORT"] = "27017"
    os.environ["MONGO_HOST"] = "localhost"
    os.environ["MONGO_USER"] = "mongo"
    os.environ["MONGO_PASSWORD"] = "mongo"
    os.environ["MONGO_DATABASE"] = "database"
    os.environ["MONGO_AUTH_SOURCE"] = "admin"
    os.environ["SECRET_KEY"] = "some_secret"
    from api.api import app

    return TestClient(app)
