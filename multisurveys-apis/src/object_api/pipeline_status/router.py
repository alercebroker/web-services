import logging

from fastapi import APIRouter, HTTPException

from . import service, settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/pipeline_status", summary="Is each pipeline processing alerts, and how many arrived recently")
def pipeline_status(scenario: str | None = None):
    """For each pipeline (`lsst`, `ztf`):

    - `state`: `up_to_date` (new alerts are processed as they arrive), `processing` (a backlog of alerts is
      being processed), `no_data` (the survey sent no alerts in the last `no_data_window`) or `unknown`.
    - `lag`: alerts waiting to be processed, over all its steps.
    - `alerts[window]`: alerts received in that window; `processed[window]`: alerts its first step consumed.
      `null` when the window is longer than the metrics history.

    Useful before asking for "the latest N objects": while a pipeline is `processing`, recent data is still
    coming in. Alerts are not objects (an object gets one alert per detection), and processed alerts take a
    few minutes to become searchable. Refreshed at most once a minute.

    Returns `{"enabled": false}` when the feature is not configured. `scenario` is only for demos with
    simulated data (mixed, processing, up_to_date, no_data) and is ignored otherwise.
    """
    try:
        return service.get_status(scenario if settings.SOURCE == "fake" else None)
    except service.StatusUnavailable:
        # Already logged where it failed. Don't leak Prometheus details (URL, auth errors) to the browser.
        raise HTTPException(status_code=503, detail="Pipeline status is temporarily unavailable")
    except Exception:
        logger.exception("pipeline_status: unexpected error")
        raise HTTPException(status_code=503, detail="Pipeline status is temporarily unavailable")
