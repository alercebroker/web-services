"""Where the raw numbers come from: Prometheus, or a simulation for demos.

Both sources return the same ``Snapshot`` and ``Activity``, so the logic that turns numbers into a status
(``service.py``) is the same for real and simulated data.

- ``Snapshot``: what is happening now (messages waiting, when the last alert arrived and was processed).
- ``Activity``: how many alerts arrived and were processed in one time span (``since``), queried per span
  so each one is cached on its own.
"""

import math
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import requests

from . import settings


@dataclass
class Snapshot:
    # (consumer group, topic) -> messages waiting
    lag: dict[tuple[str, str], float] = field(default_factory=dict)
    # topic -> unix time its end offset last grew (an alert arrived); missing if not in LAST_SEEN_LOOKBACK
    last_received: dict[str, float] = field(default_factory=dict)
    # consumer group -> unix time its offset last grew (it consumed an alert)
    last_processed: dict[str, float] = field(default_factory=dict)
    # How far back Prometheus keeps data, if it says so.
    retention_seconds: float | None = None


@dataclass
class Activity:
    # topic -> messages written to the topic in the span
    alerts: dict[str, float] = field(default_factory=dict)
    # consumer group -> messages consumed in the span
    processed: dict[str, float] = field(default_factory=dict)


_DURATION = re.compile(r"(\d+)([smhdwy])")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}


def duration_seconds(text: str) -> float | None:
    """Seconds in a Prometheus duration ("1h", "15d", "1d12h"). None if there is none."""
    parts = _DURATION.findall(text or "")
    if not parts:
        return None
    return sum(int(n) * _UNIT_SECONDS[u] for n, u in parts)


# ─── Prometheus ───────────────────────────────────────────────────────────────


def _labels(*extra: str, instance: str = "") -> str:
    labels = list(extra)
    if instance:
        labels.append(f'instance="{instance}"')
    return "{" + ", ".join(labels) + "}"


def _auth():
    return (settings.PROMETHEUS_USER, settings.PROMETHEUS_PASSWORD) if settings.PROMETHEUS_USER else None


def _query(promql: str) -> list[dict]:
    response = requests.get(
        f"{settings.PROMETHEUS_URL}/api/v1/query",
        params={"query": promql},
        auth=_auth(),
        timeout=settings.TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def _retention_seconds() -> float | None:
    try:
        response = requests.get(
            f"{settings.PROMETHEUS_URL}/api/v1/status/runtimeinfo", auth=_auth(), timeout=settings.TIMEOUT_SECONDS
        )
        response.raise_for_status()
        # e.g. "15d" or "15d or 100GiB": the time part is what limits our windows
        return duration_seconds(response.json()["data"].get("storageRetention", "").split(" or ")[0])
    except (requests.RequestException, KeyError, ValueError):
        # Optional: without it, every span is reported.
        return None


def _by(result: list[dict], *keys: str) -> dict:
    out = {}
    for series in result:
        key = tuple(series["metric"].get(k, "") for k in keys)
        out[key if len(keys) > 1 else key[0]] = float(series["value"][1])
    return out


def _selectors() -> tuple[str, str]:
    """(reflector topics' end offsets, ingestion groups' offsets)."""
    topics = "|".join(p.reflector_topic for p in settings.PIPELINES)
    log_end = _labels('name="LogEndOffset"', f'topic=~"{topics}"', instance=settings.JMX_INSTANCE)
    # Group names are plain [a-z0-9_-], so no regex escaping (a backslash would also need
    # escaping inside the PromQL string).
    ingestion = "|".join(p.ingestion_group for p in settings.PIPELINES)
    offsets = _labels(f'consumergroup=~"{ingestion}"', instance=settings.KAFKA_EXPORTER_INSTANCE)
    return f"kafka_log_log_value{log_end}", f"kafka_consumergroup_current_offset_sum{offsets}"


def _last_change(series: str, by: str) -> str:
    # The last minute (within LAST_SEEN_LOOKBACK) in which the offset grew. Offsets only go up, so "changed" means
    # an alert was written (end offset) or consumed (group offset). One-minute precision.
    lookback = settings.LAST_SEEN_LOOKBACK
    return f"max by ({by}) (max_over_time((timestamp(changes({series}[2m]) > 0))[{lookback}:1m]))"


def snapshot_from_prometheus() -> Snapshot:
    log_end, offsets = _selectors()
    groups = _labels('topic!~"^_.*"', instance=settings.KAFKA_EXPORTER_INSTANCE)
    queries = {
        "lag": f"sum by (consumergroup, topic) (kafka_consumergroup_lag_sum{groups})",
        "last_received": _last_change(log_end, "topic"),
        "last_processed": _last_change(offsets, "consumergroup"),
    }
    with ThreadPoolExecutor(max_workers=4) as pool:
        retention = pool.submit(_retention_seconds)
        results = dict(zip(queries, pool.map(_query, queries.values())))

    return Snapshot(
        lag=_by(results["lag"], "consumergroup", "topic"),
        last_received=_by(results["last_received"], "topic"),
        last_processed=_by(results["last_processed"], "consumergroup"),
        retention_seconds=retention.result(),
    )


def activity_from_prometheus(since: str) -> Activity:
    log_end, offsets = _selectors()
    # Growth of each topic's end offset = messages written in the span (same as the Grafana panels), and growth of
    # the ingestion groups' offsets = messages they consumed. One query: the two halves have different labels
    # (topic / consumergroup), so `or` keeps both.
    result = _query(
        f"(sum by (topic) (max_over_time({log_end}[{since}]) - min_over_time({log_end}[{since}])))"
        f" or (sum by (consumergroup) (max_over_time({offsets}[{since}]) - min_over_time({offsets}[{since}])))"
    )
    return Activity(
        alerts=_by([s for s in result if "topic" in s["metric"]], "topic"),
        processed=_by([s for s in result if "consumergroup" in s["metric"]], "consumergroup"),
    )


# ─── Simulation ───────────────────────────────────────────────────────────────

# A few real-looking groups per pipeline: (group, topic it reads).
_FAKE_GROUPS = {
    "lsst": [
        ("lsst-ingestion", "lsst-v11.1"),
        ("lsst-correction", "lsst-ingestion-v11.1"),
        ("lsst-magstats", "lsst-correction-v11.1"),
        ("features-ms", "lsst-magstats-v11.1"),
        ("scribe-multisurvey", "scribe-multisurvey-v11.1"),
    ],
    "ztf": [
        ("ztf-ingestion", "ztf-reflector"),
        ("ztf-correction", "ztf-ingestion"),
        ("ztf-magstats", "ztf-correction"),
        ("features-ms-ztf", "ztf-magstats-p256"),
        ("lc-classifier-ms-ztf-bhrf", "ztf-features"),
    ],
}
_FAKE_TOPICS = {"lsst": "lsst-v11.1", "ztf": "ztf"}
# Alerts per hour each pipeline receives while the survey is observing.
_FAKE_RATE = {"lsst": 400_000, "ztf": 60_000}
# In the no_data scenario, the last alerts arrived this long ago.
_FAKE_SILENCE_SECONDS = 3 * 86400

# What each pipeline is doing in each scenario.
FAKE_SCENARIOS = {
    "mixed": {"lsst": "processing", "ztf": "up_to_date"},
    "processing": {"lsst": "processing", "ztf": "processing"},
    "up_to_date": {"lsst": "up_to_date", "ztf": "up_to_date"},
    "no_data": {"lsst": "no_data", "ztf": "no_data"},
}


def _wave(now: float) -> float:
    return (math.sin(now / 90) + 1) / 2  # 0..1, a full cycle every ~9 minutes


def _ingestion_group(pid: str) -> str:
    return next(p.ingestion_group for p in settings.PIPELINES if p.id == pid)


def simulated_snapshot(scenario: str = "mixed", now: float | None = None) -> Snapshot:
    """Plausible numbers that move over time, so a demo looks live."""
    now = time.time() if now is None else now
    states = FAKE_SCENARIOS.get(scenario, FAKE_SCENARIOS["mixed"])
    snap = Snapshot(retention_seconds=5 * 86400)  # like production's Prometheus

    for pid, groups in _FAKE_GROUPS.items():
        state = states[pid]
        for i, (group, topic) in enumerate(groups):
            # A backlog shrinking down the pipeline while processing; a few stray messages otherwise.
            snap.lag[(group, topic)] = round(5_000 * (0.5 + _wave(now)) / (i + 1)) if state == "processing" else i % 2
        last = now - _FAKE_SILENCE_SECONDS if state == "no_data" else now - 30
        snap.last_received[_FAKE_TOPICS[pid]] = last
        snap.last_processed[_ingestion_group(pid)] = last + 20
    return snap


def simulated_activity(since: str, scenario: str = "mixed", now: float | None = None) -> Activity:
    now = time.time() if now is None else now
    states = FAKE_SCENARIOS.get(scenario, FAKE_SCENARIOS["mixed"])
    hours = duration_seconds(since) / 3600
    activity = Activity()
    for pid in _FAKE_GROUPS:
        state, rate = states[pid], _FAKE_RATE[pid]
        silent_hours = _FAKE_SILENCE_SECONDS / 3600
        share = max(0.0, (hours - silent_hours) / hours) if state == "no_data" else 1.0
        # Surveys observe about 8 hours a night.
        count = round(rate * min(hours, 8 * max(1, hours // 24)) * share * (0.9 + 0.2 * _wave(now)))
        activity.alerts[_FAKE_TOPICS[pid]] = count
        activity.processed[_ingestion_group(pid)] = round(count * (0.97 if state == "processing" else 1))
    return activity
