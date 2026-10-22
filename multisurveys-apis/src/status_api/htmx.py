"""The pipeline status card, served as HTML for the explorer like the other cards (magstat, crossmatch, ...).

The explorer only puts an htmx container in its header; this route renders the card, and the card refreshes
itself (every minute, or with its buttons) by asking this route again.
"""

from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.static_files import configure_templates

from .router import _status

router = APIRouter()
templates = Jinja2Templates(directory="src/status_api/templates", autoescape=True, auto_reload=True)
configure_templates(templates, "http://localhost:8008")

# The windows the card offers, all asked for in one request (the API caches the answer for a minute)
WINDOWS = ["15m", "30m", "1h", "3h", "6h", "12h", "24h", "3d", "7d"]
DEFAULT_WINDOW = "12h"
# Labels and messages come from the service; only the dot colours are decided here
COLORS = {"up_to_date": "#00e676", "processing": "#ffc107", "no_data": "#9e9e9e", "unknown": "#616161"}


def _time(iso: str | None) -> str | None:
    return datetime.fromisoformat(iso).strftime("%H:%M UTC") if iso else None


def _count(n: int | None) -> str:
    return "–" if n is None else f"{n:,}"


@router.get("/htmx/pipeline_status", response_class=HTMLResponse, include_in_schema=False)
def pipeline_status_card(
    request: Request,
    window: str = Query(DEFAULT_WINDOW),
    scenario: str | None = Query(None),
):
    status = _status(",".join(WINDOWS), scenario)  # 503 when not configured or Prometheus fails
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
                    "last_alert": _time(p["last_alert_received_at"]),
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
