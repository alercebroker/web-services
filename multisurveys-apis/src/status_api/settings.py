"""Settings for the status API.

What changes between deployments comes from ``PIPELINE_STATUS_*`` environment variables, set in the
``environment:`` block of the API's ``config.yaml`` (or its Helm values). Nothing secret lives in this file.

Which consumer groups belong to which pipeline, and the rules that turn metrics into a status, are configured
here, in code, because they change rarely and are easiest to review as a diff.
"""

import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StatusSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIPELINE_STATUS_", env_ignore_empty=True)

    source: Literal["prometheus", "fake"] | None = Field(
        None,
        description="`prometheus` reads real metrics, `fake` serves simulated ones (demos, local testing). "
        "Unset: every request answers 503.",
    )
    prometheus_url: str = Field("", description="Prometheus base URL.")
    prometheus_user: str = Field("", description="Basic auth user, if Prometheus needs it. Use a read-only user.")
    prometheus_password: SecretStr = Field(SecretStr(""), description="Basic auth password.")
    kafka_exporter_instance: str = Field(
        "", description='Optional `instance` label of the kafka exporter, e.g. "<host>:9308".'
    )
    jmx_instance: str = Field(
        "", description='Optional `instance` label of the Kafka JMX exporter, e.g. "<host>:7071".'
    )
    cache_seconds: float = Field(60, gt=0, description="Seconds an answer is reused before it is refreshed.")
    timeout_seconds: float = Field(
        10, gt=0, description="Timeout of each Prometheus request. The last-alert queries scan days of samples."
    )
    retry_after_failure_seconds: float = Field(
        30, ge=0, description="After Prometheus fails, seconds before it is asked again (not on every request)."
    )
    max_stale_seconds: float = Field(
        600, gt=0, description="While Prometheus fails, the last good answer is served for at most this long."
    )
    max_cache_entries: int = Field(64, gt=0, description="Most time spans whose counts are cached at once.")

    @field_validator("source", mode="before")
    @classmethod
    def _normalize_source(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("prometheus_url")
    @classmethod
    def _strip_slash(cls, value: str) -> str:
        return value.rstrip("/")


settings = StatusSettings()

# A pipeline with at least this many messages waiting (over all its steps) is "processing" a backlog. Smaller
# leftovers (a group sitting at lag 1 forever) still count as up to date.
BACKLOG_MIN_LAG = 100
# A pipeline that received no alerts in this window (and has no backlog) shows "no recent data".
NO_DATA_WINDOW = "2d"
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
    _topic: re.Pattern | None = field(default=None, repr=False)

    def __post_init__(self):
        self._compiled = [re.compile(p) for p in self.group_patterns]
        self._topic = re.compile(self.reflector_topic)

    def owns(self, group: str) -> bool:
        return any(p.search(group) for p in self._compiled)

    def receives_on(self, topic: str) -> bool:
        return self._topic.fullmatch(topic) is not None


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
