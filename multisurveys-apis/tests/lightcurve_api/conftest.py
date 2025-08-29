import os

from db_plugins.db.sql.models import Object
import pytest
from fastapi.testclient import TestClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from core.config.connection import ApiDatabase
from core.repository.queries.create_q3c_index import create_q3c_idx
from lightcurve_api.api import app
from faker import Faker

from db_plugins.db.sql._connection import PsqlDatabase
from sqlalchemy import text
from core.idmapper import idmapper


@pytest.fixture(scope="session")
def db_setup():
    with DockerImage(
        path=".",
        dockerfile_path="Dockerfile-psql",
        tag="base-psql:latest",
        clean_up=False,
    ) as image:
        with (
            DockerContainer(str(image))
            .with_env("POSTGRES_DB", "multistream")
            .with_env("POSTGRES_USER", "alerce")
            .with_env("POSTGRES_PASSWORD", "alerce")
            .with_exposed_ports("5432/tcp") as container
        ):
            wait_for_logs(
                container,
                "ready to accept connections",
                timeout=10,
            )

            host = container.get_container_host_ip()
            os.environ["PSQL_USER"] = "alerce"
            os.environ["PSQL_PASSWORD"] = "alerce"
            os.environ["PSQL_DATABASE"] = "multistream"
            os.environ["PSQL_HOST"] = host
            os.environ["PSQL_PORT"] = str(
                container.get_exposed_port("5432/tcp")
            )
            db = ApiDatabase()
            db.create_db()
            create_q3c_idx(db)
            yield db
            db.drop_db()


@pytest.fixture(scope="session")
def client(db_setup):
    return TestClient(app)


@pytest.fixture(scope="function")
def populate_database(faker: Faker, db_setup: PsqlDatabase):
    def _populate(n=100):
        objects = [
            Object(
                oid=idmapper.catalog_oid_to_masterid(
                    "ZTF", "ZTF20aaelulu"
                ).item(),
                tid=1,
                sid=1,
                meanra=faker.latitude(),
                meandec=faker.longitude(),
                firstmjd=faker.random_int(min=59000, max=61000),
                lastmjd=faker.random_int(min=59000, max=61000),
                deltamjd=faker.random_int(min=0, max=365),
                n_det=faker.random_int(min=0, max=100),
                n_forced=faker.random_int(min=0, max=100),
                n_non_det=faker.random_int(min=0, max=100),
                corrected=faker.boolean(),
            )
        ]
        for _ in range(n):
            objects.append(
                Object(
                    oid=idmapper.catalog_oid_to_masterid(
                        "ZTF",
                        f"ZTF{faker.year()[2:]}{''.join(faker.random_letters(7))}",
                    ).item(),
                    tid=1,
                    sid=1,
                    meanra=faker.latitude(),
                    meandec=faker.longitude(),
                    firstmjd=faker.random_int(min=59000, max=61000),
                    lastmjd=faker.random_int(min=59000, max=61000),
                    deltamjd=faker.random_int(min=0, max=365),
                    n_det=faker.random_int(min=0, max=100),
                    n_forced=faker.random_int(min=0, max=100),
                    n_non_det=faker.random_int(min=0, max=100),
                    corrected=faker.boolean(),
                )
            )
        with db_setup.session() as session:
            session.add_all(objects)
            session.commit()

    yield _populate
    with db_setup.session() as session:
        session.execute(text("DELETE FROM object"))
        session.commit()
