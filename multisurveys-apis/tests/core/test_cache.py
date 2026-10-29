import threading
import time

import pytest

from core import cache
from core.cache import StaleWhileRevalidateCache, Unavailable


def make(**options):
    defaults = dict(
        name="test",
        fresh_seconds=60,
        retry_after_failure_seconds=30,
        max_stale_seconds=600,
        wait_seconds=1,
        max_entries=8,
    )
    return StaleWhileRevalidateCache(**{**defaults, **options})


@pytest.fixture(autouse=True)
def quiet(monkeypatch):
    monkeypatch.setattr(cache.logger, "exception", lambda *a, **k: None)


class Upstream:
    def __init__(self, fail=False, delay=0.0):
        self.calls = 0
        self.fail = fail
        self.delay = delay

    def __call__(self):
        self.calls += 1
        time.sleep(self.delay)
        if self.fail:
            raise RuntimeError("down")
        return f"value {self.calls}"


def test_a_fresh_value_is_reused():
    c, upstream = make(), Upstream()
    assert c.get("k", upstream)[0] == "value 1"
    assert c.get("k", upstream)[0] == "value 1"
    assert upstream.calls == 1


def test_a_stale_value_is_refreshed():
    c, upstream = make(), Upstream()
    c.get("k", upstream)
    c._entries["k"].at -= 61
    assert c.get("k", upstream)[0] == "value 2"


def test_nobody_waits_for_a_refresh_in_progress(monkeypatch):
    c, upstream = make(), Upstream()
    c.get("k", upstream)
    entry = c._entries["k"]
    entry.at = 1.0  # old, but within max_stale_seconds of "now" below
    monkeypatch.setattr(cache.time, "time", lambda: 1.0 + 61)
    assert entry.lock.acquire(blocking=False)  # another request is refreshing
    try:
        assert c.get("k", upstream) == ("value 1", 1.0)  # the old value, right away
    finally:
        entry.lock.release()
    assert upstream.calls == 1


def test_first_request_waits_for_the_one_fetching_then_gives_up():
    c = make(wait_seconds=0.05)
    entry = c._entry("k")
    assert entry.lock.acquire(blocking=False)  # another request is fetching, and never finishes
    try:
        with pytest.raises(Unavailable):
            c.get("k", Upstream())
    finally:
        entry.lock.release()


def test_failures_are_not_retried_on_every_request():
    c, upstream = make(), Upstream(fail=True)
    for _ in range(3):
        with pytest.raises(Unavailable):
            c.get("k", upstream)
    assert upstream.calls == 1


def test_requests_queued_behind_a_failed_fetch_dont_fetch_again():
    c, upstream = make(), Upstream(fail=True, delay=0.2)
    errors = []

    def request():
        try:
            c.get("k", upstream)
        except Unavailable as e:
            errors.append(e)

    threads = [threading.Thread(target=request) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert upstream.calls == 1
    assert len(errors) == 5


def test_the_last_value_is_served_while_the_upstream_fails_then_dropped(monkeypatch):
    c = make()
    c.get("k", Upstream())
    entry = c._entries["k"]
    entry.at = 1.0
    monkeypatch.setattr(cache.time, "time", lambda: 1.0 + 300)
    assert c.get("k", Upstream(fail=True))[0] == "value 1"
    monkeypatch.setattr(cache.time, "time", lambda: 1.0 + 601)
    with pytest.raises(Unavailable):
        c.get("k", Upstream(fail=True))


def test_size_is_bounded():
    c = make(max_entries=4)
    for n in range(20):
        c.get(f"k{n}", Upstream())
    assert len(c) == 4


def test_an_entry_being_fetched_is_not_evicted():
    c = make(max_entries=4)
    fetching = c._entry("busy")
    assert fetching.lock.acquire(blocking=False)  # a request is fetching it, so it has no value yet (at=0)
    try:
        for n in range(20):
            c.get(f"k{n}", Upstream())
        assert c._entries.get("busy") is fetching
    finally:
        fetching.lock.release()


def test_clear():
    c = make()
    c.get("k", Upstream())
    c.clear()
    assert len(c) == 0
