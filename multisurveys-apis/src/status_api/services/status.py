"""Turns raw Kafka metrics into a per-pipeline status, meant for users ("is the data current?").

The response only has per-pipeline totals: nothing about individual steps reaches this public API.
"""

import time
from concurrent.futures import ThreadPoolExecutor

from core.cache import StaleWhileRevalidateCache, Unavailable

from core.exceptions import StatusNotConfigured, StatusUnavailable
from ..models.status import Activity, Availability, PipelineState, PipelineStatus, Scenario, Status
from ..settings import BACKLOG_MIN_LAG, EXCLUDED_GROUPS, NO_DATA_WINDOW, PIPELINES, Pipeline, settings
from . import prometheus, simulation
from .formatting import duration_seconds, human_duration, iso, short_duration

_cache_options = dict(
    fresh_seconds=settings.cache_seconds,
    retry_after_failure_seconds=settings.retry_after_failure_seconds,
    max_stale_seconds=settings.max_stale_seconds,
    wait_seconds=settings.timeout_seconds * 2,
)
snapshots = StaleWhileRevalidateCache("status_api snapshot", max_entries=1, **_cache_options)
activities = StaleWhileRevalidateCache("status_api activity", max_entries=settings.max_cache_entries, **_cache_options)

# Shared by all requests: the activity spans of one request are queried in parallel
_activity_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="status-activity")


def clear_cache():
    snapshots.clear()
    activities.clear()


def assign_groups(lag: dict[tuple[str, str], float]) -> dict[str, dict[str, float]]:
    """Pipeline id -> {consumer group: messages waiting}, summed over the topics each group reads."""
    owned: dict[str, dict[str, float]] = {p.id: {} for p in PIPELINES}
    for (group, _topic), waiting in lag.items():
        if EXCLUDED_GROUPS.match(group):
            continue
        pipeline = next((p for p in PIPELINES if p.owns(group)), None)
        if pipeline is not None:
            owned[pipeline.id][group] = owned[pipeline.id].get(group, 0.0) + waiting
    return owned


def pipeline_state(
    has_groups: bool, has_topic: bool, lag: float, last_received: float | None, now: float
) -> PipelineState:
    """`has_groups`: lag metrics for any of the pipeline's consumer groups. `has_topic`: an end offset for its
    reflector topic. Without either, missing alerts can't be told apart from missing metrics.
    """
    if not has_groups:
        return PipelineState.UNKNOWN
    if lag >= BACKLOG_MIN_LAG:
        return PipelineState.PROCESSING
    if last_received is None and not has_topic:
        return PipelineState.UNKNOWN
    if last_received is None or now - last_received > duration_seconds(NO_DATA_WINDOW):
        return PipelineState.NO_DATA
    return PipelineState.UP_TO_DATE


def describe(state: PipelineState, lag: int) -> tuple[str, str]:
    """(short label, one sentence for users)."""
    match state:
        case PipelineState.PROCESSING:
            return "Processing backlog", f"{lag:,} alerts are waiting to be processed: recent data is still coming in."
        case PipelineState.NO_DATA:
            return (
                "No recent data",
                f"No alerts received in the last {human_duration(duration_seconds(NO_DATA_WINDOW))}.",
            )
        case PipelineState.UP_TO_DATE:
            return "Up to date", "New alerts are processed as they arrive."
        case PipelineState.UNKNOWN:
            return "Unknown", "The metrics for this pipeline are not available right now, so its state is unknown."


def within_history(snapshot: prometheus.Snapshot, since: str) -> bool:
    # A span as long as Prometheus' retention (or longer) would silently undercount.
    return snapshot.retention_seconds is None or duration_seconds(since) < snapshot.retention_seconds


def _matching(values: dict[str, float], pipeline: Pipeline) -> list[float]:
    return [v for topic, v in values.items() if pipeline.receives_on(topic)]


def _activity_of(
    pipeline: Pipeline, snapshot: prometheus.Snapshot, since: str, counts: prometheus.Activity | None
) -> Activity:
    if not within_history(snapshot, since):
        return Activity(availability=Availability.BEYOND_HISTORY, alerts_received=None, alerts_processed=None)
    if counts is None:
        return Activity(availability=Availability.UNAVAILABLE, alerts_received=None, alerts_processed=None)
    received = _matching(counts.alerts, pipeline)
    processed = counts.processed.get(pipeline.ingestion_group)
    return Activity(
        availability=Availability.AVAILABLE,
        alerts_received=int(sum(received)) if received else None,
        alerts_processed=None if processed is None else int(processed),
    )


def build_status(
    snapshot: prometheus.Snapshot,
    since: list[str],
    activity: dict[str, prometheus.Activity | None],
    updated_at: float,
    simulated: bool = False,
) -> Status:
    """`activity` has the counts of each span read, or None if reading them failed. Spans beyond the history
    are left out of it.
    """
    owned = assign_groups(snapshot.lag)
    pipelines = []
    for p in PIPELINES:
        lag = int(sum(owned[p.id].values()))
        last_received = max(_matching(snapshot.last_received, p), default=None)
        has_topic = bool(_matching(snapshot.end_offsets, p))
        state = pipeline_state(bool(owned[p.id]), has_topic, lag, last_received, updated_at)
        label, message = describe(state, lag)
        pipelines.append(
            PipelineStatus(
                survey=p.id,
                name=p.name,
                status=state,
                status_label=label,
                message=message,
                alerts_waiting=lag,
                last_alert_received_at=iso(last_received),
                last_alert_processed_at=iso(snapshot.last_processed.get(p.ingestion_group)),
                activity={s: _activity_of(p, snapshot, s, activity.get(s)) for s in since},
            )
        )

    return Status(
        updated_at=iso(updated_at),
        history_available=short_duration(snapshot.retention_seconds) if snapshot.retention_seconds else None,
        pipelines=pipelines,
        simulated=simulated,
    )


def _activity(since: str) -> prometheus.Activity | None:
    try:
        value, _ = activities.get(since, lambda: prometheus.activity_from_prometheus(since))
        return value
    except Unavailable:
        # The counts are extra: without them, the status itself is still worth answering.
        return None


def get_status(since: list[str], scenario: Scenario | None = None) -> Status:
    if settings.source is None:
        raise StatusNotConfigured()
    since = list(dict.fromkeys(since))
    if settings.source == "fake":
        now = time.time()
        snapshot = simulation.simulated_snapshot(scenario or "mixed", now)
        activity = {s: simulation.simulated_activity(s, scenario or "mixed", now) for s in since}
        return build_status(snapshot, since, activity, now, simulated=True)

    try:
        snapshot, updated_at = snapshots.get("snapshot", prometheus.snapshot_from_prometheus)
    except Unavailable as e:
        raise StatusUnavailable() from e
    wanted = [s for s in since if within_history(snapshot, s)]
    activity = dict(zip(wanted, _activity_pool.map(_activity, wanted)))
    return build_status(snapshot, since, activity, updated_at)
