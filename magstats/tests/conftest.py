import pytest
import os
import pathlib
import psycopg2
from pymongo import MongoClient
from pymongo.database import Database
from db_plugins.db.sql._connection import PsqlDatabase as DbpDatabase
from db_plugins.db.mongo._connection import MongoConnection
from fastapi.testclient import TestClient
from db_plugins.db.sql.models import Object, MagStats

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
            / "magstats/tests/docker-compose.yml"
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
        add_psql_magstats(session)

def add_psql_objects(session):
    object = Object(oid="oid1")
    object2 = Object(oid="oid2")
    session.add(object)
    session.add(object2)
    session.commit()


def add_psql_magstats(session):
    magstats = [
        {
            "fid": 123,
            "oid": "oid1",
            "stellar": False,
            "corrected": False,
            "ndet": 1,
            "ndubious": 1,
            "dmdt_first": 0.13,
            "dm_first": 0.12,
            "sigmadm_first": 1.4,
            "dt_first": 2.0,
            "magmean": 19.0,
            "magmedian": 20,
            "magmax": 1.4,
            "magmin": 1.4,
            "magsigma": 1.4,
            "maglast": 1.4,
            "magfirst": 1.4,
            "firstmjd": 1.4,
            "lastmjd": 1.4,
            "step_id_corr": "test",
        },
        {
            "fid": 456,
            "oid": "oid2",
            "stellar": False,
            "corrected": False,
            "ndet": 1,
            "ndubious": 1,
            "dmdt_first": 0.13,
            "dm_first": 0.12,
            "sigmadm_first": 1.4,
            "dt_first": 2.0,
            "magmean": 19.0,
            "magmedian": 20,
            "magmax": 1.4,
            "magmin": 1.4,
            "magsigma": 1.4,
            "maglast": 1.4,
            "magfirst": 1.4,
            "firstmjd": 1.4,
            "lastmjd": 1.4,
            "step_id_corr": "test",
        },

    ]
    magstats = [MagStats(**mag) for mag in magstats]
    session.add_all(magstats)
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
    add_mongo_magstats(database.database)

def add_mongo_objects(database: Database):
    object1 = {
        "_id": "aid1",
        "oid": ["oid1", "oid2"],
    }
    database["object"].insert_one(object1)

def add_mongo_magstats(database: Database):
    magstats = [
        {
            "_id": "candid1",
            "aid": "aid1",
            "oid": "oid1",
            "tid": "atlas",
        },
        {
            "_id": "candid2",
            "aid": "aid1",
            "tid": "atlas",
            "oid": "oid1",
        },
        {
            "_id": "candid3",
            "aid": "aid1",
            "tid": "atlas",
            "oid": "oid2",
        },
        {
            "_id": "candid4",
            "aid": "aid1",
            "tid": "atlas",
            "oid": "oid2",
        },

    ]
    for mag in magstats:
        database.magstats.insert_one(mag)
        
def teardown_mongo(database: MongoConnection):
    database.drop_db()

@pytest.fixture(scope="session")
def test_client():
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