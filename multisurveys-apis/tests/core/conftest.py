import os

import pytest
from sqlalchemy import text
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from core.config.connection import psql_entity
from core.repository.queries.create_q3c_index import create_q3c_idx


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
            print(f"Connecting to {host}:{os.environ['PSQL_PORT']}")
            db = psql_entity()
            db.create_db()
            create_q3c_idx(db)
            yield db
            db.drop_db()


@pytest.fixture(scope="function")
def db(db_setup):
    yield db_setup

    with db_setup.session() as session:
        session.execute(text("DELETE FROM ztf_detection"))
        session.execute(text("DELETE FROM lsst_detection"))
        session.execute(text("DELETE FROM detection"))
        session.execute(text("DELETE FROM ztf_non_detection"))
        session.execute(text("DELETE FROM forced_photometry"))
        session.execute(text("DELETE FROM ztf_forced_photometry"))
        session.execute(text("DELETE FROM lsst_forced_photometry"))
        session.execute(text("DELETE FROM object"))
        session.commit()
