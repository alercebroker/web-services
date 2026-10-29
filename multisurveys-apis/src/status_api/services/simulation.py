"""Simulated metrics for demos and local testing (``PIPELINE_STATUS_SOURCE=fake``)."""

import math
import time

from ..models.status import PipelineState
from ..settings import PIPELINES
from .formatting import duration_seconds
from .prometheus import Activity, Snapshot

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

# What each pipeline is doing in each scenario. In `unknown`, the JMX exporter reports nothing.
FAKE_SCENARIOS = {
    "mixed": {"lsst": PipelineState.PROCESSING, "ztf": PipelineState.UP_TO_DATE},
    "processing": {"lsst": PipelineState.PROCESSING, "ztf": PipelineState.PROCESSING},
    "up_to_date": {"lsst": PipelineState.UP_TO_DATE, "ztf": PipelineState.UP_TO_DATE},
    "no_data": {"lsst": PipelineState.NO_DATA, "ztf": PipelineState.NO_DATA},
    "unknown": {"lsst": PipelineState.UNKNOWN, "ztf": PipelineState.UNKNOWN},
}


def _wave(now: float) -> float:
    return (math.sin(now / 90) + 1) / 2  # 0..1, a full cycle every ~9 minutes


def _ingestion_group(pid: str) -> str:
    return next(p.ingestion_group for p in PIPELINES if p.id == pid)


def simulated_snapshot(scenario: str = "mixed", now: float | None = None) -> Snapshot:
    """Plausible numbers that move over time, so a demo looks live."""
    now = time.time() if now is None else now
    states = FAKE_SCENARIOS.get(scenario, FAKE_SCENARIOS["mixed"])
    snap = Snapshot(retention_seconds=5 * 86400)  # like production's Prometheus

    for pid, groups in _FAKE_GROUPS.items():
        state = states[pid]
        for i, (group, topic) in enumerate(groups):
            # A backlog shrinking down the pipeline while processing; a few stray messages otherwise.
            processing = state == PipelineState.PROCESSING
            snap.lag[(group, topic)] = round(5_000 * (0.5 + _wave(now)) / (i + 1)) if processing else i % 2
        last = now - _FAKE_SILENCE_SECONDS if state == PipelineState.NO_DATA else now - 30
        snap.last_processed[_ingestion_group(pid)] = last + 20
        if state != PipelineState.UNKNOWN:
            snap.end_offsets[_FAKE_TOPICS[pid]] = round(now)
            snap.last_received[_FAKE_TOPICS[pid]] = last
    return snap


def simulated_activity(since: str, scenario: str = "mixed", now: float | None = None) -> Activity:
    now = time.time() if now is None else now
    states = FAKE_SCENARIOS.get(scenario, FAKE_SCENARIOS["mixed"])
    hours = duration_seconds(since) / 3600
    activity = Activity()
    for pid in _FAKE_GROUPS:
        state, rate = states[pid], _FAKE_RATE[pid]
        silent_hours = _FAKE_SILENCE_SECONDS / 3600
        share = max(0.0, (hours - silent_hours) / hours) if state == PipelineState.NO_DATA else 1.0
        # Surveys observe about 8 hours a night.
        count = round(rate * min(hours, 8 * max(1, hours // 24)) * share * (0.9 + 0.2 * _wave(now)))
        if state == PipelineState.UNKNOWN:
            activity.processed[_ingestion_group(pid)] = 0
            continue
        activity.alerts[_FAKE_TOPICS[pid]] = count
        activity.processed[_ingestion_group(pid)] = round(count * (0.97 if state == PipelineState.PROCESSING else 1))
    return activity
