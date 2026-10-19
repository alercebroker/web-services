"""Turns raw Kafka metrics into a per-pipeline status, meant for users ("is the data current?").

- processing:  at least ``BACKLOG_MIN_LAG`` alerts waiting over all its steps: catching up.
- no_data:     no backlog, and the survey sent no alerts in ``NO_DATA_WINDOW``.
- up_to_date:  otherwise: new alerts are processed as they arrive.
- unknown:     no metrics for any of its consumer groups.

The response only has per-pipeline totals: nothing about individual steps reaches this public API.
"""

import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime

from . import metrics, settings

logger = logging.getLogger(__name__)


class StatusUnavailable(Exception):
    """No status to give right now (Prometheus failing and nothing recent cached)."""


class InvalidSince(ValueError):
    """`since` is not a list of durations we accept. The message is shown to the user."""


# ─── Status ───────────────────────────────────────────────────────────────────


def assign_groups(lag: dict[tuple[str, str], float]) -> dict[str, dict[str, float]]:
    """Pipeline id -> {consumer group: messages waiting}, summed over the topics each group reads."""
    owned: dict[str, dict[str, float]] = {p.id: {} for p in settings.PIPELINES}
    for (group, _topic), waiting in lag.items():
        if settings.EXCLUDED_GROUPS.match(group):
            continue
        pipeline = next((p for p in settings.PIPELINES if p.owns(group)), None)
        if pipeline is not None:
            owned[pipeline.id][group] = owned[pipeline.id].get(group, 0.0) + waiting
    return owned


def pipeline_state(has_groups: bool, lag: float, last_received: float | None, now: float) -> str:
    if not has_groups:
        return "unknown"
    if lag >= settings.BACKLOG_MIN_LAG:
        return "processing"
    if last_received is None or now - last_received > metrics.duration_seconds(settings.NO_DATA_WINDOW):
        return "no_data"
    return "up_to_date"


def human_duration(seconds: float) -> str:
    """86400*2 -> "2 days", 3600 -> "1 hour"."""
    for unit, size in (("day", 86400), ("hour", 3600), ("minute", 60)):
        if seconds >= size and seconds % size == 0:
            n = int(seconds // size)
            return f"{n} {unit}{'s' if n != 1 else ''}"
    return f"{int(seconds)} seconds"


def short_duration(seconds: float) -> str:
    """86400*5 -> "5d", 5400 -> "90m"."""
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if seconds >= size and seconds % size == 0:
            return f"{int(seconds // size)}{unit}"
    return f"{int(seconds)}s"


def describe(state: str, lag: int) -> tuple[str, str]:
    """(short label, one sentence for users)."""
    if state == "processing":
        return "Processing backlog", f"{lag:,} alerts are waiting to be processed: recent data is still coming in."
    if state == "no_data":
        window = human_duration(metrics.duration_seconds(settings.NO_DATA_WINDOW))
        return "No recent data", f"No alerts received in the last {window}."
    if state == "up_to_date":
        return "Up to date", "New alerts are processed as they arrive."
    return "Unknown", "No metrics are available for this pipeline right now."


def iso(ts: float | None) -> str | None:
    return None if ts is None else datetime.fromtimestamp(ts, tz=UTC).isoformat(timespec="seconds")


_SINCE = re.compile(r"^[1-9][0-9]*[mhd]$")


def parse_since(text: str | None) -> list[str]:
    """ "1h, 24h" -> ["1h", "24h"]. Raises InvalidSince with a message for the user."""
    if text is None or not text.strip():
        return list(settings.DEFAULT_SINCE)
    spans = list(dict.fromkeys(s.strip() for s in text.split(",") if s.strip()))
    if len(spans) > settings.MAX_SINCE_PER_REQUEST:
        raise InvalidSince(f"At most {settings.MAX_SINCE_PER_REQUEST} durations per request.")
    for s in spans:
        if not _SINCE.match(s):
            raise InvalidSince(f"'{s}' is not a duration: use a number and m, h or d, like 30m, 6h or 3d.")
        if metrics.duration_seconds(s) > settings.MAX_SINCE_SECONDS:
            raise InvalidSince(f"'{s}' is too long: at most {short_duration(settings.MAX_SINCE_SECONDS)}.")
    return spans


def build_status(
    snapshot: metrics.Snapshot,
    activity: dict[str, metrics.Activity | None],
    updated_at: float,
    simulated: bool = False,
) -> dict:
    """`activity` maps each requested span to its counts, or None if unavailable (longer than the history)."""
    owned = assign_groups(snapshot.lag)
    pipelines = []
    for p in settings.PIPELINES:
        topic = re.compile(p.reflector_topic)
        lag = int(sum(owned[p.id].values()))
        last_received = max((t for name, t in snapshot.last_received.items() if topic.fullmatch(name)), default=None)
        last_processed = snapshot.last_processed.get(p.ingestion_group)
        state = pipeline_state(bool(owned[p.id]), lag, last_received, updated_at)
        label, message = describe(state, lag)

        spans = {}
        for since, counts in activity.items():
            if counts is None:
                spans[since] = {"alerts_received": None, "alerts_processed": None}
            else:
                spans[since] = {
                    "alerts_received": int(sum(v for t, v in counts.alerts.items() if topic.fullmatch(t))),
                    "alerts_processed": int(counts.processed.get(p.ingestion_group, 0)),
                }

        pipelines.append(
            {
                "survey": p.id,
                "name": p.name,
                "status": state,
                "status_label": label,
                "message": message,
                "alerts_waiting": lag,
                "last_alert_received_at": iso(last_received),
                "last_alert_processed_at": iso(last_processed),
                "activity": spans,
            }
        )

    status = {
        "updated_at": iso(updated_at),
        "history_available": short_duration(snapshot.retention_seconds) if snapshot.retention_seconds else None,
        "pipelines": pipelines,
    }
    if simulated:
        status["simulated"] = True
    return status


# ─── Cached entry point ───────────────────────────────────────────────────────


@dataclass
class _Entry:
    value: object = None
    at: float = 0.0
    failed_at: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)


_entries: dict[str, _Entry] = {}
_entries_lock = threading.Lock()
# Bounds memory: users can ask for any span, and each distinct one gets an entry.
MAX_CACHE_ENTRIES = 64


def clear_cache():
    with _entries_lock:
        _entries.clear()


def _entry(key: str) -> _Entry:
    with _entries_lock:
        if key not in _entries:
            if len(_entries) >= MAX_CACHE_ENTRIES:
                oldest = min((k for k in _entries if k != "snapshot"), key=lambda k: _entries[k].at, default=None)
                _entries.pop(oldest, None)
            _entries[key] = _Entry()
        return _entries[key]


def _cached(key: str, fetch) -> tuple[object, float]:
    """(value, when it was fetched). Reused for CACHE_SECONDS.

    Only one request refreshes a stale value, and the others get the stale one without waiting: the API allows few
    requests at once per pod, so requests queueing behind a slow Prometheus would make it answer "busy". When there
    is no value yet, requests wait for the one fetching it. If Prometheus fails, retry after
    RETRY_AFTER_FAILURE_SECONDS, and serve the last value for at most MAX_STALE_SECONDS.
    """
    entry = _entry(key)
    if entry.value is not None and time.time() - entry.at < settings.CACHE_SECONDS:
        return entry.value, entry.at

    if time.time() - entry.failed_at >= settings.RETRY_AFTER_FAILURE_SECONDS:
        first = entry.value is None
        if entry.lock.acquire(blocking=first, timeout=settings.TIMEOUT_SECONDS * 2 if first else -1):
            try:
                # Another request may have refreshed it while this one waited.
                if entry.value is None or time.time() - entry.at >= settings.CACHE_SECONDS:
                    entry.value, entry.at = fetch(), time.time()
            except Exception:
                entry.failed_at = time.time()
                logger.exception("status_api: could not read %s from Prometheus", key)
            finally:
                entry.lock.release()

    if entry.value is None or time.time() - entry.at > settings.MAX_STALE_SECONDS:
        raise StatusUnavailable()
    return entry.value, entry.at


def _available(snapshot: metrics.Snapshot, since: str) -> bool:
    # A span as long as Prometheus' retention (or longer) would silently undercount: report it as unavailable.
    return snapshot.retention_seconds is None or metrics.duration_seconds(since) < snapshot.retention_seconds


def _activity(since: str) -> metrics.Activity | None:
    # Keyed by length, so "60m" and "1h" share an entry.
    try:
        value, _ = _cached(f"since:{metrics.duration_seconds(since)}", lambda: metrics.activity_from_prometheus(since))
        return value
    except StatusUnavailable:
        # The counts are extra: without them, the status itself is still worth answering.
        return None


def get_status(since: list[str], scenario: str | None = None) -> dict:
    if settings.SOURCE == "fake":
        now = time.time()
        snapshot = metrics.simulated_snapshot(scenario or "mixed", now)
        activity = {
            s: metrics.simulated_activity(s, scenario or "mixed", now) if _available(snapshot, s) else None
            for s in since
        }
        return build_status(snapshot, activity, now, simulated=True)

    snapshot, updated_at = _cached("snapshot", metrics.snapshot_from_prometheus)
    wanted = [s for s in since if _available(snapshot, s)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        counts = dict(zip(wanted, pool.map(_activity, wanted)))
    activity = {s: counts.get(s) for s in since}
    return build_status(snapshot, activity, updated_at)
