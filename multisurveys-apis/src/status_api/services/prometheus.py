"""Where the raw numbers come from: Prometheus, with fixed queries.

The simulation (``simulation.py``) returns the same ``Snapshot`` and ``Activity``, so the logic that turns
numbers into a status (``status.py``) is the same for real and simulated data.

- ``Snapshot``: what is happening now (messages waiting, when the last alert arrived and was processed).
- ``Activity``: how many alerts arrived and were processed in one time span (``since``), queried per span
  so each one is cached on its own.
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import requests

from ..settings import LAST_SEEN_LOOKBACK, PIPELINES, settings
from .formatting import duration_seconds


@dataclass
class Snapshot:
    # (consumer group, topic) -> messages waiting
    lag: dict[tuple[str, str], float] = field(default_factory=dict)
    # topic -> its end offset now; a topic is missing when the JMX exporter doesn't report it
    end_offsets: dict[str, float] = field(default_factory=dict)
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


def _labels(*extra: str, instance: str = "") -> str:
    labels = list(extra)
    if instance:
        labels.append(f'instance="{instance}"')
    return "{" + ", ".join(labels) + "}"


def _auth():
    if not settings.prometheus_user:
        return None
    return settings.prometheus_user, settings.prometheus_password.get_secret_value()


def _query(promql: str) -> list[dict]:
    response = requests.get(
        f"{settings.prometheus_url}/api/v1/query",
        params={"query": promql},
        auth=_auth(),
        timeout=settings.timeout_seconds,
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def _retention_seconds() -> float | None:
    try:
        response = requests.get(
            f"{settings.prometheus_url}/api/v1/status/runtimeinfo", auth=_auth(), timeout=settings.timeout_seconds
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
    topics = "|".join(p.reflector_topic for p in PIPELINES)
    log_end = _labels('name="LogEndOffset"', f'topic=~"{topics}"', instance=settings.jmx_instance)
    # Group names are plain [a-z0-9_-], so no regex escaping (a backslash would also need
    # escaping inside the PromQL string).
    ingestion = "|".join(p.ingestion_group for p in PIPELINES)
    offsets = _labels(f'consumergroup=~"{ingestion}"', instance=settings.kafka_exporter_instance)
    return f"kafka_log_log_value{log_end}", f"kafka_consumergroup_current_offset_sum{offsets}"


def _last_change(series: str, by: str) -> str:
    # The last minute (within LAST_SEEN_LOOKBACK) in which the offset grew. Offsets only go up, so "changed" means
    # an alert was written (end offset) or consumed (group offset). One-minute precision.
    return f"max by ({by}) (max_over_time((timestamp(changes({series}[2m]) > 0))[{LAST_SEEN_LOOKBACK}:1m]))"


def snapshot_from_prometheus() -> Snapshot:
    log_end, offsets = _selectors()
    groups = _labels('topic!~"^_.*"', instance=settings.kafka_exporter_instance)
    queries = {
        "lag": f"sum by (consumergroup, topic) (kafka_consumergroup_lag_sum{groups})",
        "end_offsets": f"max by (topic) ({log_end})",
        "last_received": _last_change(log_end, "topic"),
        "last_processed": _last_change(offsets, "consumergroup"),
    }
    with ThreadPoolExecutor(max_workers=len(queries) + 1) as pool:
        retention = pool.submit(_retention_seconds)
        results = dict(zip(queries, pool.map(_query, queries.values())))

    return Snapshot(
        lag=_by(results["lag"], "consumergroup", "topic"),
        end_offsets=_by(results["end_offsets"], "topic"),
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
