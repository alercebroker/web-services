"""Fixtures shared by every test folder."""

import time

import psycopg2
import pytest


def _wait_for_postgres(host, port, user="alerce", password="alerce", database="multistream", timeout=30):
    """Poll until a real connection to PostgreSQL succeeds.

    PostgreSQL logs "ready to accept connections" twice on a fresh container: once for the temporary server that
    runs the init scripts, then for the real one after a restart. wait_for_logs() returns on the first one, and a
    connection then hits the restart ("server closed the connection unexpectedly").
    """
    deadline = time.time() + timeout
    while True:
        try:
            psycopg2.connect(
                host=host, port=port, user=user, password=password, dbname=database, connect_timeout=2
            ).close()
            return
        except psycopg2.OperationalError:
            if time.time() > deadline:
                raise
            time.sleep(0.5)


@pytest.fixture(scope="session")
def wait_for_postgres():
    """``wait_for_postgres(host, port)``: see _wait_for_postgres."""
    return _wait_for_postgres
