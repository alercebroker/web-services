import os
import pytest
import psycopg2

from core.shared.sql import Database, Session
from core.infrastructure.orm import Object, Probability
from core.infrastructure.astroobject_sql_repository import AstroObjectSQLRespository
from db.utils import create_database, delete_database


@pytest.fixture(scope="session")
def docker_compose_command():
    compose_version = os.getenv("COMPOSE_VERSION", "v1")
    if compose_version == "v1":
        return "docker-compose"
    return "docker compose"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "tests/integration", "docker-compose.yaml"
    )


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
        "DATABASE": "postgres",
    }
    database = Database(db_config)
    populate_database(database)
    astro_repo = AstroObjectSQLRespository(database)
    yield astro_repo
    delete_database(database._engine)


def populate_database(db: Database):
    create_database(db._engine)
    with db.session() as session:
        add_objects(session)
        add_probabilities(session)


def add_objects(session: Session):
    obj = Object(oid="ZTF123")
    session.add(obj)
    session.commit()


def add_probabilities(session: Session):
    probs = [
        {
            "oid": "ZTF123",
            "class_name": "SNIa",
            "classifier_name": "classifier_lol",
            "classifier_version": "v1",
            "probability": 0.70,
            "ranking": 1
        },
        {
            "oid": "ZTF123",
            "class_name": "Other",
            "classifier_name": "classifier_lol",
            "classifier_version": "v1",
            "probability": 0.30,
            "ranking": 2
        },
    ]
    orm_probs = [Probability(**prob) for prob in probs]
    session.add_all(orm_probs)
    session.commit()
