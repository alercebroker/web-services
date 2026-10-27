from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from . import service, settings

router = APIRouter()

SINCE_HELP = (
    "Time spans to count alerts in, separated by commas: a number and m (minutes), h (hours) or d (days), "
    f"like `30m`, `6h,24h` or `3d`. Default: `{','.join(settings.DEFAULT_SINCE)}`."
)
# Only for demos with simulated data (PIPELINE_STATUS_SOURCE=fake): ignored otherwise, so not in /docs
Scenario = Literal["mixed", "processing", "up_to_date", "no_data"]


@router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return "OK"


def _status(since: str | None, scenario: Scenario | None) -> dict:
    if not settings.enabled():
        raise HTTPException(status_code=503, detail="The status API is not configured")
    try:
        spans = service.parse_since(since)
    except service.InvalidSince as e:
        raise HTTPException(status_code=422, detail=str(e))
    try:
        return service.get_status(spans, scenario if settings.SOURCE == "fake" else None)
    except service.StatusUnavailable:
        # Already logged where it failed. Don't leak Prometheus details (URL, auth errors) to the browser.
        raise HTTPException(status_code=503, detail="Pipeline status is temporarily unavailable")


@router.get("/pipeline_status", summary="Is each pipeline up to date, and how many alerts it received and processed")
def pipeline_status(
    since: str | None = Query(None, description=SINCE_HELP),
    scenario: Scenario | None = Query(None, include_in_schema=False),
):
    """For each pipeline (`lsst`, `ztf`):

    - `status`: `up_to_date` (new alerts are processed as they arrive), `processing` (a backlog of alerts is
      being processed, so recent data is still coming in), `no_data` (the survey sent no alerts in the last
      2 days) or `unknown`. `status_label` and `message` say the same in words.
    - `alerts_waiting`: alerts waiting to be processed.
    - `last_alert_received_at` / `last_alert_processed_at`: when the last alert arrived and when the pipeline
      last processed one (UTC, one-minute precision). `null` if none in the last 7 days.
    - `activity[since]`: `alerts_received` and `alerts_processed` in each requested span. `null` when the span
      is longer than `history_available` (how far back the metrics go).

    Alerts are not objects: an object gets one alert per detection, and processed alerts take a few minutes to
    become searchable. Refreshed at most once a minute, so asking more often gives the same answer.
    """
    return _status(since, scenario)


@router.get("/pipeline_status/{survey}", summary="Status of one pipeline")
def pipeline_status_one(
    survey: str,
    since: str | None = Query(None, description=SINCE_HELP),
    scenario: Scenario | None = Query(None, include_in_schema=False),
):
    """The same as `/pipeline_status`, for one survey (`lsst` or `ztf`)."""
    ids = [p.id for p in settings.PIPELINES]
    if survey.lower() not in ids:
        raise HTTPException(status_code=404, detail=f"Unknown survey '{survey}': use one of {', '.join(ids)}.")
    status = _status(since, scenario)
    one = next(p for p in status.pop("pipelines") if p["survey"] == survey.lower())
    return {**status, "pipeline": one}
