import pytest
import os
import pathlib
import psycopg2
from db_plugins.db.sql._connection import PsqlDatabase as DbpDatabase
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


@pytest.fixture(scope="session")
def test_client():
    os.environ["PSQL_PORT"] = "5432"
    os.environ["PSQL_HOST"] = "localhost"
    os.environ["PSQL_USER"] = "postgres"
    os.environ["PSQL_PASSWORD"] = "postgres"
    os.environ["PSQL_DATABASE"] = "postgres"
    os.environ["SECRET_KEY"] = "some_secret"
    from api.api import app

    return TestClient(app)
