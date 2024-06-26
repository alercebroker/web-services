import pytest
import pathlib
import psycopg
from psycopg_pool import ConnectionPool
import os

@pytest.fixture(scope="session")
def docker_compose_file():
    return pathlib.Path("tests/docker-compose.yaml")

def is_responsive_psql(url):
    try:
        conn = psycopg.connect(
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

def create_tables(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE mastercat (
                    id text,
                    ipix bigint,
                    ra double precision,
                    dec double precision,
                    cat text,
                    PRIMARY KEY (id, cat)
                )
                """
            )

def create_indices(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE INDEX ON mastercat (ipix)")

def delete_tables(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE mastercat")

@pytest.fixture
def init_database(psql_service):
    conn_url = "postgresql://postgres:postgres@localhost:5432/postgres"
    pool = ConnectionPool(conninfo=conn_url, open=True)
    create_tables(pool)
    create_indices(pool)
    yield 
    delete_tables(pool)

@pytest.fixture
def env_setup():
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "postgres"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_DATABASE"] = "postgres"
    yield
    os.environ.pop("DB_USER")
    os.environ.pop("DB_PASSWORD")
    os.environ.pop("DB_HOST")
    os.environ.pop("DB_PORT")
    os.environ.pop("DB_DATABASE")

