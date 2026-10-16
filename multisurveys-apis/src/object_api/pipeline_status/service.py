"""Turns raw Kafka metrics into a per-pipeline status, meant for users ("is the data current?").

- processing:  at least ``BACKLOG_MIN_LAG`` alerts waiting over all its steps: catching up.
- no_data:     no backlog, and the survey sent no alerts in ``NO_DATA_WINDOW``.
- up_to_date:  otherwise: new alerts are processed as they arrive.
- unknown:     no metrics for any of its consumer groups.

The response only has per-pipeline totals: nothing about individual steps reaches this public endpoint.
"""

import logging
import re
import threading
import time
from datetime import UTC, datetime

from . import metrics, settings

logger = logging.getLogger(__name__)


class StatusUnavailable(Exception):
    """No status to give right now (Prometheus failing and nothing recent cached)."""


def assign_groups(raw: metrics.RawMetrics) -> dict[str, dict[str, float]]:
    """Pipeline id -> {consumer group: messages waiting}, summed over the topics each group reads."""
    owned: dict[str, dict[str, float]] = {p.id: {} for p in settings.PIPELINES}
    for (group, _topic), lag in raw.lag.items():
        if settings.EXCLUDED_GROUPS.match(group):
            continue
        pipeline = next((p for p in settings.PIPELINES if p.owns(group)), None)
        if pipeline is not None:
            owned[pipeline.id][group] = owned[pipeline.id].get(group, 0.0) + lag
    return owned


def pipeline_state(has_groups: bool, lag: float, recent_alerts: float | None) -> str:
    if not has_groups:
        return "unknown"
    if lag >= settings.BACKLOG_MIN_LAG:
        return "processing"
    if recent_alerts == 0:
        return "no_data"
    return "up_to_date"


def build_status(raw: metrics.RawMetrics, source: str, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    owned = assign_groups(raw)

    # A window as long as Prometheus' retention (or longer) would silently undercount: report it as unavailable.
    def available(window: str) -> bool:
        return raw.retention_seconds is None or metrics.duration_seconds(window) < raw.retention_seconds

    def received(p: settings.Pipeline, window: str) -> int | None:
        if not available(window):
            return None
        topic = re.compile(p.reflector_topic)
        return int(sum(v for t, v in raw.alerts.get(window, {}).items() if topic.fullmatch(t)))

    pipelines = []
    for p in settings.PIPELINES:
        lag = int(sum(owned[p.id].values()))
        pipelines.append(
            {
                "id": p.id,
                "name": p.name,
                "state": pipeline_state(bool(owned[p.id]), lag, received(p, settings.NO_DATA_WINDOW)),
                "lag": lag,
                "alerts": {w: received(p, w) for w in settings.WINDOWS},
                "processed": {
                    w: (int(raw.processed.get(w, {}).get(p.ingestion_group, 0)) if available(w) else None)
                    for w in settings.WINDOWS
                },
            }
        )

    return {
        "enabled": True,
        "source": source,
        "updated_at": datetime.fromtimestamp(now, tz=UTC).isoformat(timespec="seconds"),
        "windows": settings.WINDOWS,
        "no_data_window": settings.NO_DATA_WINDOW,
        "pipelines": pipelines,
    }


# ─── Cached entry point ───────────────────────────────────────────────────────

_lock = threading.Lock()
_cache: dict = {"at": 0.0, "status": None, "failed_at": 0.0}


def get_status(scenario: str | None = None) -> dict:
    if not settings.enabled():
        return {"enabled": False}

    if settings.SOURCE == "fake":
        return build_status(metrics.simulated(scenario or "mixed"), source="fake")

    now = time.time()
    if _cache["status"] is not None and now - _cache["at"] < settings.CACHE_SECONDS:
        return _cache["status"]

    # Only one request refreshes, and nobody waits for it: the API allows few requests at once per pod, so
    # requests queueing behind a slow Prometheus would make the object API itself answer "busy".
    retry_due = now - _cache["failed_at"] >= settings.RETRY_AFTER_FAILURE_SECONDS
    if retry_due and _lock.acquire(blocking=False):
        try:
            _cache["status"] = build_status(metrics.from_prometheus(), source="prometheus")
            _cache["at"] = time.time()
        except Exception:
            _cache["failed_at"] = time.time()
            logger.exception("pipeline_status: could not read metrics from Prometheus")
        finally:
            _lock.release()

    if _cache["status"] is None or time.time() - _cache["at"] > settings.MAX_STALE_SECONDS:
        raise StatusUnavailable()
    return _cache["status"]
