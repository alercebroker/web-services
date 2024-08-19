import os
import pytest
import psycopg2

from sqlalchemy.orm import Session
from core.infrastructure.astroobject_sql_repository import AstroObjectSQLRespository
from core.shared.sql import Database
from db_plugins.db.sql.models import Object, Probability

import pathlib

from db_plugins.db.sql._connection import PsqlDatabase


@pytest.fixture(scope="session")
def docker_compose_command():
    compose_version = os.getenv("COMPOSE_VERSION", "v1")
    if compose_version == "v1":
        return "docker-compose"
    return "docker compose"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    print(pytestconfig.rootdir)
    assert False
    try:
        path = (
            pathlib.Path(pytestconfig.rootdir) / "tests/integration/docker-compose.yaml"
        )
        assert path.exists()
        return path
    except AssertionError:
        path = (
            pathlib.Path(pytestconfig.rootdir)
            / "astroobject/tests/integration/docker-compose.yaml"
        )
        assert path.exists()
        return path


def is_psql_responsive():
    try:
        connection = psycopg2.connect(
            "dbname='postgres' user='postgres' host=localhost password='postgres'"
        )
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False


@pytest.fixture(scope="session")
def psql_service(docker_ip, docker_services):
    port = docker_services.port_for("postgres", 5432)
    server = f"{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_psql_responsive()
    )
    return server


@pytest.fixture
def astro_repository():
    db_config = {
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "DB_NAME": "postgres",
        "DATABASE": "postgres",
    }
    database = PsqlDatabase(db_config)
    populate_database(database)
    core_database = Database(db_config)
    astro_repo = AstroObjectSQLRespository(core_database)
    yield astro_repo
    database.drop_db()


def populate_database(db: PsqlDatabase):
    db.create_db()
    add_objects(db)
    add_probabilities(db)


def add_objects(db: PsqlDatabase):
    with db.session() as session:
        obj = Object(oid="ZTF123")
        session.add(obj)
        session.commit()


def add_probabilities(db: PsqlDatabase):
    probs = [
        {
            "oid": "ZTF123",
            "class_name": "SNIa",
            "classifier_name": "classifier_lol",
            "classifier_version": "v1",
            "probability": 0.70,
            "ranking": 1,
        },
        {
            "oid": "ZTF123",
            "class_name": "Other",
            "classifier_name": "classifier_lol",
            "classifier_version": "v1",
            "probability": 0.30,
            "ranking": 2,
        },
        {
            "oid": "ZTF123",
            "class_name": "E",
            "classifier_name": "classifier_kek",
            "classifier_version": "v1",
            "probability": 0.69,
            "ranking": 1,
        },
        {
            "oid": "ZTF123",
            "class_name": "Other/Class",
            "classifier_name": "classifier_kek",
            "classifier_version": "v1",
            "probability": 0.31,
            "ranking": 2,
        },
    ]
    with db.session() as session:
        orm_probs = [Probability(**prob) for prob in probs]
        session.add_all(orm_probs)
        session.commit()
