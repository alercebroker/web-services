"""A thread-safe stale-while-revalidate cache for slow upstreams."""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Unavailable(Exception):
    """No value recent enough to serve: never fetched, or the last good one is older than `max_stale_seconds`."""


@dataclass
class _Entry:
    value: object = None
    at: float = 0.0
    failed_at: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)


class StaleWhileRevalidateCache(Generic[T]):
    """Values are reused for `fresh_seconds`. Only one request refreshes a stale value, and the others get the stale
    one without waiting: requests queueing behind a slow upstream would fill the pod's request slots. When there is
    no value yet, requests wait up to `wait_seconds` for the one fetching it. After a failed fetch, the upstream is
    asked again only after `retry_after_failure_seconds`, and the last value is served for at most
    `max_stale_seconds`.
    """

    def __init__(
        self,
        name: str,
        fresh_seconds: float,
        retry_after_failure_seconds: float,
        max_stale_seconds: float,
        wait_seconds: float,
        max_entries: int,
    ):
        self.name = name
        self.fresh_seconds = fresh_seconds
        self.retry_after_failure_seconds = retry_after_failure_seconds
        self.max_stale_seconds = max_stale_seconds
        self.wait_seconds = wait_seconds
        self.max_entries = max_entries
        self._entries: dict[str, _Entry] = {}
        self._lock = threading.Lock()

    def __len__(self) -> int:
        return len(self._entries)

    def clear(self):
        with self._lock:
            self._entries.clear()

    def _entry(self, key: str) -> _Entry:
        with self._lock:
            if key not in self._entries:
                if len(self._entries) >= self.max_entries:
                    # Not one being fetched right now: its result would land in an entry no longer in the cache
                    evictable = (k for k, e in self._entries.items() if not e.lock.locked())
                    oldest = min(evictable, key=lambda k: self._entries[k].at, default=None)
                    self._entries.pop(oldest, None)
                self._entries[key] = _Entry()
            return self._entries[key]

    def get(self, key: str, fetch: Callable[[], T]) -> tuple[T, float]:
        """(value, when it was fetched). Raises `Unavailable` when there is nothing recent enough to serve."""
        entry = self._entry(key)
        if entry.value is not None and time.time() - entry.at < self.fresh_seconds:
            return entry.value, entry.at

        if time.time() - entry.failed_at >= self.retry_after_failure_seconds:
            first = entry.value is None
            if entry.lock.acquire(blocking=first, timeout=self.wait_seconds if first else -1):
                try:
                    # Another request may have refreshed it, or failed to, while this one waited.
                    stale = entry.value is None or time.time() - entry.at >= self.fresh_seconds
                    failed_recently = time.time() - entry.failed_at < self.retry_after_failure_seconds
                    if stale and not failed_recently:
                        entry.value, entry.at = fetch(), time.time()
                except Exception:
                    entry.failed_at = time.time()
                    logger.exception("%s: could not fetch %s", self.name, key)
                finally:
                    entry.lock.release()

        if entry.value is None or time.time() - entry.at > self.max_stale_seconds:
            raise Unavailable(key)
        return entry.value, entry.at
