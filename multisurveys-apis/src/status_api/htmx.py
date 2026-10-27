"""The pipeline status card, served as HTML for the explorer like the other cards (magstat, crossmatch, ...).

The explorer only puts an htmx container in its header; this route renders the card, and the card refreshes
itself (every minute, or with its buttons) by asking this route again.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from core.static_files import configure_templates, html_templates

from . import service, settings
from .router import Scenario

router = APIRouter()
templates = html_templates("src/status_api/templates")
configure_templates(templates, "http://localhost:8008")

# The windows the card offers, all asked for in one request (the API caches the answer for a minute)
WINDOWS = ["15m", "30m", "1h", "3h", "6h", "12h", "24h", "3d", "7d"]
DEFAULT_WINDOW = "12h"
# Labels and messages come from the service; only the dot colours are decided here
COLORS = {"up_to_date": "#00e676", "processing": "#ffc107", "no_data": "#9e9e9e", "unknown": "#616161"}


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
    scenario: Scenario | None = Query(None, include_in_schema=False),
):
    if not settings.enabled():
        raise HTTPException(status_code=503, detail="The status API is not configured")
    try:
        status = service.get_status(WINDOWS, scenario if settings.SOURCE == "fake" else None)
    except service.StatusUnavailable:
        # A card saying so, not an error: htmx doesn't swap error answers, so the card would stay empty or stale
        return templates.TemplateResponse(
            request,
            "pipeline_status.html.jinja",
            {"unavailable": True, "window": window, "scenario": scenario},
        )
    pipelines = status["pipelines"]
    available = [w for w in WINDOWS if any(p["activity"][w]["alerts_received"] is not None for p in pipelines)]
    if window not in available:
        window = DEFAULT_WINDOW if DEFAULT_WINDOW in available else (available[0] if available else DEFAULT_WINDOW)

    return templates.TemplateResponse(
        request,
        "pipeline_status.html.jinja",
        {
            "pipelines": [
                {
                    **p,
                    "color": COLORS.get(p["status"], COLORS["unknown"]),
                    "last_alert": _time(p["last_alert_received_at"], status["updated_at"]),
                    "received": _count(p["activity"][window]["alerts_received"]),
                    "processed": _count(p["activity"][window]["alerts_processed"]),
                }
                for p in pipelines
            ],
            "windows": [{"name": w, "available": w in available} for w in WINDOWS],
            "window": window,
            "scenario": scenario,
            "simulated": status.get("simulated", False),
            "updated": datetime.fromisoformat(status["updated_at"]).strftime("%H:%M:%S UTC"),
        },
    )
