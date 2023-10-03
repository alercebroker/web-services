import os
import pathlib

import psycopg2
import pytest
from db_plugins.db.mongo._connection import MongoConnection
from db_plugins.db.sql._connection import PsqlDatabase as DbpDatabase
from db_plugins.db.sql.models import Detection, NonDetection, Object
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.database import Database


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
    populate_psql(dbp_database)
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
    os.environ["SECRET_KEY"] = "some_secret"
    from database.mongo import database

    return database


def populate_psql(database):
    database.create_db()
    with database.session() as session:
        add_psql_objects(session)
        add_psql_detections(session)
        add_psql_non_detections(session)


def add_psql_objects(session):
    object = Object(oid="oid1")
    session.add(object)
    session.commit()


def add_psql_detections(session):
    detections = [
        {
            "candid": 123,
            "oid": "oid1",
            "mjd": 59000,
            "fid": 1,
            "pid": 1,
            "isdiffpos": 1,
            "ra": 10,
            "dec": 20,
            "magpsf": 15,
            "sigmapsf": 0.5,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
            "step_id_corr": "test",
        },
        {
            "candid": 456,
            "oid": "oid1",
            "mjd": 59001,
            "fid": 2,
            "pid": 1,
            "isdiffpos": 1,
            "ra": 11,
            "dec": 21,
            "magpsf": 14,
            "sigmapsf": 0.4,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
            "step_id_corr": "test",
        },
    ]
    detections = [Detection(**det) for det in detections]
    session.add_all(detections)
    session.commit()


def add_psql_non_detections(session):
    non_detections = [
        {"oid": "oid1", "mjd": 59000, "fid": 1, "diffmaglim": 0.5},
        {"oid": "oid1", "mjd": 59001, "fid": 2, "diffmaglim": 0.4},
    ]
    non_detections = [NonDetection(**non) for non in non_detections]
    session.add_all(non_detections)
    session.commit()


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
    populate_mongo(db)
    yield db.client.database
    teardown_mongo(db)


def populate_mongo(database: MongoConnection):
    database.create_db()
    add_mongo_objects(database.database)
    add_mongo_detections(database.database)


def add_mongo_objects(database: Database):
    object1 = {
        "_id": "aid1",
        "oid": ["oid1", "oid2"],
    }
    database["object"].insert_one(object1)


def add_mongo_detections(database: Database):
    detections = [
        {
            "_id": "candid1",
            "aid": "aid1",
            "oid": "oid1",
            "tid": "atlas",
            "mjd": 59000,
            "fid": 1,
            "ra": 10,
            "dec": 20,
            "mag": 15,
            "e_mag": 0.5,
            "isdiffpos": 1,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
        },
        {
            "_id": "candid2",
            "aid": "aid1",
            "tid": "atlas",
            "oid": "oid1",
            "mjd": 59001,
            "fid": 2,
            "ra": 11,
            "dec": 21,
            "mag": 14,
            "e_mag": 0.4,
            "isdiffpos": 1,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
        },
        {
            "_id": "candid3",
            "aid": "aid2",
            "tid": "atlas",
            "oid": "oid2",
            "mjd": 59005,
            "fid": 3,
            "ra": 12.0,
            "e_ra": 0.1,
            "dec": 22.0,
            "e_dec": 0.2,
            "mag": 13.0,
            "e_mag": 0.3,
            "isdiffpos": 1,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
        },
        {
            "_id": "candid4",
            "aid": "aid2",
            "tid": "atlas",
            "oid": "oid2",
            "mjd": 59006,
            "fid": 3,
            "ra": 11.0,
            "e_ra": 0.2,
            "dec": 23.0,
            "e_dec": 0.3,
            "mag": 12.0,
            "e_mag": 0.4,
            "isdiffpos": 1,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
        },
    ]
    for det in detections:
        database.detection.insert_one(det)


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
    os.environ["SECRET_KEY"] = "some_secret"
    from api.api import app

    return TestClient(app)
