"""Where the raw numbers come from: Prometheus, or a simulation for demos.

Both sources return the same ``RawMetrics``, so the logic that turns numbers into a status
(``service.py``) is the same for real and simulated data.
"""

import math
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import requests

from . import settings


@dataclass
class RawMetrics:
    # (consumer group, topic) -> messages waiting
    lag: dict[tuple[str, str], float] = field(default_factory=dict)
    # window -> topic -> messages written to the topic in that window
    alerts: dict[str, dict[str, float]] = field(default_factory=dict)
    # window -> consumer group -> messages consumed in that window
    processed: dict[str, dict[str, float]] = field(default_factory=dict)
    # How far back Prometheus keeps data, if it says so.
    retention_seconds: float | None = None


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


def _query(promql: str) -> list[dict]:
    response = requests.get(
        f"{settings.PROMETHEUS_URL}/api/v1/query",
        params={"query": promql},
        auth=(settings.PROMETHEUS_USER, settings.PROMETHEUS_PASSWORD) if settings.PROMETHEUS_USER else None,
        timeout=settings.TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def _retention_seconds() -> float | None:
    try:
        response = requests.get(
            f"{settings.PROMETHEUS_URL}/api/v1/status/runtimeinfo",
            auth=(settings.PROMETHEUS_USER, settings.PROMETHEUS_PASSWORD) if settings.PROMETHEUS_USER else None,
            timeout=settings.TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        # e.g. "15d" or "15d or 100GiB": the time part is what limits our windows
        return duration_seconds(response.json()["data"].get("storageRetention", "").split(" or ")[0])
    except (requests.RequestException, KeyError, ValueError):
        # Optional: without it, every window is reported.
        return None


def _by(result: list[dict], *keys: str) -> dict:
    out = {}
    for series in result:
        key = tuple(series["metric"].get(k, "") for k in keys)
        out[key if len(keys) > 1 else key[0]] = float(series["value"][1])
    return out


def all_windows() -> list[str]:
    """The windows shown to users, plus the one that decides "no recent data"."""
    return settings.WINDOWS + [w for w in [settings.NO_DATA_WINDOW] if w not in settings.WINDOWS]


def from_prometheus() -> RawMetrics:
    kafka = settings.KAFKA_EXPORTER_INSTANCE
    groups = _labels('topic!~"^_.*"', instance=kafka)
    topics = "|".join(p.reflector_topic for p in settings.PIPELINES)
    log_end = _labels('name="LogEndOffset"', f'topic=~"{topics}"', instance=settings.JMX_INSTANCE)
    # Group names are plain [a-z0-9_-], so no regex escaping (a backslash would also need
    # escaping inside the PromQL string).
    ingestion = "|".join(p.ingestion_group for p in settings.PIPELINES)
    offsets = _labels(f'consumergroup=~"{ingestion}"', instance=kafka)

    queries = {"lag": f"sum by (consumergroup, topic) (kafka_consumergroup_lag_sum{groups})"}
    for w in all_windows():
        # Growth of each topic's end offset = messages written in the window (same as the Grafana panels),
        # and growth of the ingestion groups' offsets = messages they consumed. One query per window: the two
        # halves have different labels (topic / consumergroup), so `or` keeps both.
        queries[f"window:{w}"] = (
            f"(sum by (topic) (max_over_time(kafka_log_log_value{log_end}[{w}])"
            f" - min_over_time(kafka_log_log_value{log_end}[{w}])))"
            f" or (sum by (consumergroup) (max_over_time(kafka_consumergroup_current_offset_sum{offsets}[{w}])"
            f" - min_over_time(kafka_consumergroup_current_offset_sum{offsets}[{w}])))"
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        retention = pool.submit(_retention_seconds)
        results = dict(zip(queries, pool.map(_query, queries.values())))

    raw = RawMetrics(retention_seconds=retention.result())
    raw.lag = _by(results["lag"], "consumergroup", "topic")
    for w in all_windows():
        result = results[f"window:{w}"]
        raw.alerts[w] = _by([s for s in result if "topic" in s["metric"]], "topic")
        raw.processed[w] = _by([s for s in result if "consumergroup" in s["metric"]], "consumergroup")
    return raw


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

# What each pipeline is doing in each scenario.
FAKE_SCENARIOS = {
    "mixed": {"lsst": "processing", "ztf": "up_to_date"},
    "processing": {"lsst": "processing", "ztf": "processing"},
    "up_to_date": {"lsst": "up_to_date", "ztf": "up_to_date"},
    "no_data": {"lsst": "no_data", "ztf": "no_data"},
}


def simulated(scenario: str = "mixed", now: float | None = None) -> RawMetrics:
    """Plausible numbers that move over time, so a demo looks live."""
    now = time.time() if now is None else now
    states = FAKE_SCENARIOS.get(scenario, FAKE_SCENARIOS["mixed"])
    wave = (math.sin(now / 90) + 1) / 2  # 0..1, a full cycle every ~9 minutes
    raw = RawMetrics(retention_seconds=5 * 86400)  # like production's Prometheus

    for pid, groups in _FAKE_GROUPS.items():
        state, rate = states[pid], _FAKE_RATE[pid]
        for i, (group, topic) in enumerate(groups):
            # A backlog shrinking down the pipeline while processing; a few stray messages otherwise.
            raw.lag[(group, topic)] = round(5_000 * (0.5 + wave) / (i + 1)) if state == "processing" else i % 2

        ingestion = next(p.ingestion_group for p in settings.PIPELINES if p.id == pid)
        for w in all_windows():
            hours = duration_seconds(w) / 3600
            if state == "no_data":
                # Last alerts arrived 3 days ago.
                share = max(0.0, (hours - 72) / hours)
            else:
                share = 1.0
            count = round(rate * min(hours, 8 * max(1, hours // 24)) * share * (0.9 + 0.2 * wave))
            raw.alerts.setdefault(w, {})[_FAKE_TOPICS[pid]] = count
            raw.processed.setdefault(w, {})[ingestion] = round(count * (0.97 if state == "processing" else 1))
    return raw
