"""The pipeline status card, served as HTML for the explorer like the other cards (magstat, crossmatch, ...).

The explorer only puts an htmx container in its header; this route renders the card, and the card refreshes
itself (every minute, or with its buttons) by asking this route again.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from core.static_files import configure_templates, html_templates

from core.exceptions import StatusUnavailable
from ..models.status import SINCE_SPANS, Availability, Scenario
from ..services.status import get_status
from .parameters import simulation_scenario

router = APIRouter()
templates = html_templates("src/status_api/templates")
configure_templates(templates, "http://localhost:8008")

# The card offers every span the API accepts, all asked for in one request (the API caches the answer)
WINDOWS = SINCE_SPANS
DEFAULT_WINDOW = "12h"


def _time(iso: str | None, today: str) -> str | None:
    """'14:05 UTC' if it was on the same UTC day as `today`, else '2026-10-25 14:05 UTC'."""
    if not iso:
        return None
    when = datetime.fromisoformat(iso)
    same_day = when.date() == datetime.fromisoformat(today).date()
    return when.strftime("%H:%M UTC" if same_day else "%Y-%m-%d %H:%M UTC")


def _count(n: int | None) -> str:
    return "–" if n is None else f"{n:,}"


@router.get("/htmx/pipeline_status", response_class=HTMLResponse)
def pipeline_status_card(
    request: Request,
    window: str = Query(DEFAULT_WINDOW),
    scenario: Scenario | None = Depends(simulation_scenario),
):
    try:
        status = get_status(WINDOWS, scenario)
    except StatusUnavailable:
        # A card saying so, not an error: htmx doesn't swap error answers, so the card would stay empty or stale
        return templates.TemplateResponse(
            request,
            "pipeline_status.html.jinja",
            {"unavailable": True, "window": window, "scenario": scenario},
        )
    pipelines = status.pipelines
    # The same for every pipeline: it depends on the span, not on the survey
    availability = {w: pipelines[0].activity[w].availability for w in WINDOWS}
    selectable = [w for w in WINDOWS if availability[w] != Availability.BEYOND_HISTORY]
    if window not in selectable:
        window = DEFAULT_WINDOW if DEFAULT_WINDOW in selectable else (selectable[0] if selectable else DEFAULT_WINDOW)

    return templates.TemplateResponse(
        request,
        "pipeline_status.html.jinja",
        {
            "pipelines": [
                {
                    **p.model_dump(include={"survey", "name", "status", "status_label", "message"}),
                    "last_alert": _time(p.last_alert_received_at, status.updated_at),
                    "received": _count(p.activity[window].alerts_received),
                    "processed": _count(p.activity[window].alerts_processed),
                }
                for p in pipelines
            ],
            "windows": [{"name": w, "availability": availability[w]} for w in WINDOWS],
            "window": window,
            "counts_unavailable": availability.get(window) == Availability.UNAVAILABLE,
            "scenario": scenario,
            "simulated": status.simulated,
            "updated": datetime.fromisoformat(status.updated_at).strftime("%H:%M:%S UTC"),
        },
    )
