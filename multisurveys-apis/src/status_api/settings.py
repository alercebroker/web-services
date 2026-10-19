"""Settings for the status API.

Everything that can change between deployments (where Prometheus is, how to log in, which exporter
instances to read) comes from environment variables, set in the ``environment:`` block of the API's
``config.yaml``. Nothing secret lives in this file.

Which consumer groups belong to which pipeline, and which topic is each pipeline's reflector, is
configured here, in code, because it changes rarely and is easiest to review as a diff.
"""

import os
import re
from dataclasses import dataclass, field

# "prometheus" reads real metrics, "fake" serves simulated ones (demos, local testing).
# Unset (or anything else) disables the endpoint.
SOURCE = os.getenv("PIPELINE_STATUS_SOURCE", "").strip().lower()
PROMETHEUS_URL = os.getenv("PIPELINE_STATUS_PROMETHEUS_URL", "").rstrip("/")
PROMETHEUS_USER = os.getenv("PIPELINE_STATUS_PROMETHEUS_USER", "")
PROMETHEUS_PASSWORD = os.getenv("PIPELINE_STATUS_PROMETHEUS_PASSWORD", "")
# Optional `instance` label filters, e.g. "<host>:9308" (kafka exporter) and "<host>:7071" (JMX exporter).
KAFKA_EXPORTER_INSTANCE = os.getenv("PIPELINE_STATUS_KAFKA_EXPORTER_INSTANCE", "")
JMX_INSTANCE = os.getenv("PIPELINE_STATUS_JMX_INSTANCE", "")

# Seconds an answer is reused, so many users don't turn into many Prometheus queries.
CACHE_SECONDS = int(os.getenv("PIPELINE_STATUS_CACHE_SECONDS", "60"))
# If Prometheus fails, wait this long before trying again (instead of on every request) ...
RETRY_AFTER_FAILURE_SECONDS = 30
# ... and keep serving the last good answer for at most this long. Older than that it would mislead.
MAX_STALE_SECONDS = 600
# Timeout for each Prometheus request. The "last alert at" queries scan days of samples and take a few seconds.
TIMEOUT_SECONDS = float(os.getenv("PIPELINE_STATUS_TIMEOUT_SECONDS", "10"))

# A pipeline with at least this many messages waiting (over all its steps) is "processing" a backlog. Smaller
# leftovers (a group sitting at lag 1 forever) still count as up to date.
BACKLOG_MIN_LAG = 100
# A pipeline that received no alerts in this window (and has no backlog) shows "no recent data".
NO_DATA_WINDOW = "2d"

# `?since=` takes durations like 30m, 6h or 3d. Several can be asked at once (`?since=1h,24h`), up to this many.
# Durations longer than Prometheus keeps data are answered with null counts.
DEFAULT_SINCE = ["1h", "24h"]
MAX_SINCE_PER_REQUEST = 10
MAX_SINCE_SECONDS = 30 * 86400
# How far back to look for the last alert received / processed. Past Prometheus' retention there is nothing to find.
LAST_SEEN_LOOKBACK = "7d"

# Groups that are never part of a pipeline's status (tests, tools, reprocessing runs).
EXCLUDED_GROUPS = re.compile(r".*(local_test|alert_visualizer|predmirror|keda-bench|reprocess).*")


@dataclass
class Pipeline:
    id: str
    name: str
    # A consumer group belongs to the pipeline if it matches any of these patterns.
    group_patterns: list[str]
    # Regex for the topic(s) where the survey's alerts arrive: "alerts received" is counted there. A regex, so
    # new topic versions (lsst-v11.1 -> lsst-v12) keep counting without a code change.
    reflector_topic: str
    # The group that reads the reflector topic: its progress is "alerts processed".
    ingestion_group: str
    _compiled: list[re.Pattern] = field(default_factory=list, repr=False)

    def __post_init__(self):
        self._compiled = [re.compile(p) for p in self.group_patterns]

    def owns(self, group: str) -> bool:
        return any(p.search(group) for p in self._compiled)


# Only the multisurvey pipelines: the explorer shows their data. Order matters: a group is assigned to the
# first pipeline that matches it. Groups that match none (e.g. the legacy ZTF pipeline) are ignored.
PIPELINES = [
    Pipeline(
        id="lsst",
        name="LSST",
        group_patterns=[r"^lsst-", r"^features-ms$", r"^scribe-multisurvey$"],
        reflector_topic=r"lsst-v[0-9.]+",
        ingestion_group="lsst-ingestion",
    ),
    Pipeline(
        id="ztf",
        name="ZTF",
        group_patterns=[r"^ztf-", r"-ms-ztf", r"^features-ms-ztf$"],
        # ZTF alerts arrive in the `ztf` topic; the multisurvey pipeline reads them from there through
        # `ztf-reflector`.
        reflector_topic=r"ztf",
        ingestion_group="ztf-ingestion",
    ),
]


def enabled() -> bool:
    return SOURCE in ("prometheus", "fake")
