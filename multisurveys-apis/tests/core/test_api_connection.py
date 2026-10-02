import threading
import time

from sqlalchemy import text
from sqlalchemy.pool import NullPool

from core.config import connection
from core.config.connection import ApiDatabase, build_engine

DB_CONFIG = {"USER": "u", "PASSWORD": "p", "HOST": "h", "PORT": "5432", "DB_NAME": "d"}


def test_engine_uses_autocommit_and_nullpool():
    engine = build_engine({**DB_CONFIG, "SCHEMA": None})

    assert engine.dialect._on_connect_isolation_level == "AUTOCOMMIT"
    assert isinstance(engine.pool, NullPool)


def test_engine_sets_search_path_only_when_schema_is_set(mocker):
    create_engine = mocker.patch.object(connection, "create_engine")

    build_engine({**DB_CONFIG, "SCHEMA": "multisurvey,public"})
    assert create_engine.call_args.kwargs["connect_args"] == {"options": "-csearch_path=multisurvey,public"}

    build_engine({**DB_CONFIG, "SCHEMA": None})
    assert create_engine.call_args.kwargs["connect_args"] == {}


def test_singleton_is_built_once_under_concurrent_first_calls(monkeypatch, mocker):
    monkeypatch.setattr(ApiDatabase, "_instance", None)
    mocker.patch.object(connection, "build_engine")

    def slow_psql_database(*args, **kwargs):
        time.sleep(0.05)  # widen the race window
        return object()

    constructor = mocker.patch.object(connection, "PsqlDatabase", side_effect=slow_psql_database)
    instances = []
    threads = [threading.Thread(target=lambda: instances.append(ApiDatabase())) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert constructor.call_count == 1
    assert len({id(i) for i in instances}) == 1


def test_each_statement_runs_in_its_own_transaction(db):
    # Integration (testcontainers): under AUTOCOMMIT no BEGIN wraps the session, so two statements get
    # different transaction ids. Inside one transaction they would be equal.
    with db.session() as session:
        first = session.execute(text("SELECT txid_current()")).scalar()
        second = session.execute(text("SELECT txid_current()")).scalar()

    assert first != second
