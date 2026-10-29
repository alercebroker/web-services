from enum import StrEnum
from typing import Literal, get_args

from pydantic import BaseModel, Field

from ..settings import BACKLOG_MIN_LAG, LAST_SEEN_LOOKBACK, NO_DATA_WINDOW

Since = Literal["15m", "30m", "1h", "3h", "6h", "12h", "24h", "3d", "7d"]
SINCE_SPANS: list[str] = list(get_args(Since))
DEFAULT_SINCE: list[str] = ["1h", "24h"]

Scenario = Literal["mixed", "processing", "up_to_date", "no_data", "unknown"]


class PipelineState(StrEnum):
    UP_TO_DATE = "up_to_date"
    PROCESSING = "processing"
    NO_DATA = "no_data"
    UNKNOWN = "unknown"


class Availability(StrEnum):
    AVAILABLE = "available"
    BEYOND_HISTORY = "beyond_history"
    UNAVAILABLE = "unavailable"


class Activity(BaseModel):
    availability: Availability = Field(
        description="`available`: the counts were read. `beyond_history`: the span is longer than "
        "`history_available`, so there is nothing to count. `unavailable`: the counts could not be read right now."
    )
    alerts_received: int | None = Field(
        description="Alerts the survey sent in the span. `null` unless `available`, or when there are no metrics "
        "for the survey's topic."
    )
    alerts_processed: int | None = Field(
        description="Alerts the pipeline processed in the span. `null` unless `available`, or when there are no "
        "metrics for the pipeline's ingestion step."
    )


class PipelineStatus(BaseModel):
    survey: str = Field(description="Survey id, e.g. `lsst` or `ztf`.")
    name: str = Field(description="Survey name to show.")
    status: PipelineState = Field(
        description=f"`processing`: {BACKLOG_MIN_LAG} or more alerts waiting over all the pipeline's steps, so "
        f"recent data is still coming in. `no_data`: no backlog, and no alert received in the last "
        f"{NO_DATA_WINDOW}. `up_to_date`: new alerts are processed as they arrive. `unknown`: the metrics needed "
        "to tell are missing."
    )
    status_label: str = Field(description="`status` in a few words, ready to show.")
    message: str = Field(description="`status` in one sentence, ready to show.")
    alerts_waiting: int = Field(description="Alerts waiting to be processed, over all the pipeline's steps.")
    last_alert_received_at: str | None = Field(
        description=f"When the last alert arrived (ISO 8601, UTC, one-minute precision). `null` if none in the "
        f"last {LAST_SEEN_LOOKBACK} or in `history_available`, if shorter."
    )
    last_alert_processed_at: str | None = Field(
        description=f"When the pipeline last processed an alert (ISO 8601, UTC, one-minute precision). `null` "
        f"if none in the last {LAST_SEEN_LOOKBACK}."
    )
    activity: dict[str, Activity] = Field(description="Alert counts for each requested `since` span.")


class Status(BaseModel):
    updated_at: str = Field(description="When the metrics were read (ISO 8601, UTC).")
    history_available: str | None = Field(
        description="How far back the metrics go, e.g. `5d`. `null` if Prometheus doesn't say."
    )
    simulated: bool = Field(False, description="True when the API serves simulated data (demos).")
    pipelines: list[PipelineStatus]
