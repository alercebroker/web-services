import os
import pytest
import pytest_asyncio
import psycopg2

from sqlalchemy.ext.asyncio import AsyncSession

from core.shared.sql import Database
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


@pytest_asyncio.fixture
async def astro_repository():
    db_config = {
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "DATABASE": "postgres",
    }
    database = Database(db_config)
    await populate_database(database)
    astro_repo = AstroObjectSQLRespository(database)
    yield astro_repo
    await delete_database(database._engine)


async def populate_database(db: Database):
    async with db.session() as session:
        await create_database(db._engine)
        await add_objects(session)
        await add_probabilities(session)


async def add_objects(session: AsyncSession):
    obj = Object(oid="ZTF123")
    async with session.begin():
        session.add(obj)
        await session.commit()


async def add_probabilities(session: AsyncSession):
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
        {
            "oid": "ZTF123",
            "class_name": "E",
            "classifier_name": "classifier_kek",
            "classifier_version": "v1",
            "probability": 0.69,
            "ranking": 1
        },
        {
            "oid": "ZTF123",
            "class_name": "Other/Class",
            "classifier_name": "classifier_kek",
            "classifier_version": "v1",
            "probability": 0.31,
            "ranking": 2
        },
    ]
    orm_probs = [Probability(**prob) for prob in probs]
    async with session.begin():
        session.add_all(orm_probs)
        await session.commit()
