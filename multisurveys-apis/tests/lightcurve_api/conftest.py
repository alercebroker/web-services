import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from core.config.connection import psql_entity
from lightcurve_api.api import app


@pytest.fixture
def client():
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
            db = psql_entity()
            db.create_db()
            with db.session() as session:
                session.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS object_q3c_ang2ipix_idx ON object (q3c_ang2ipix(meanra, meandec));"
                    )
                )
                session.execute(
                    text("CLUSTER object_q3c_ang2ipix_idx ON object;")
                )
                session.execute(text("ANALYZE object;"))
                session.commit()

                yield TestClient(app)
