import os

from datetime import date

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from toolz import curry, pipe

from core.config.dependencies import db_dependency
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.periodogram import Periodogram
from lightcurve_api.services.lightcurve_plot_service import (
    service as lightcurve_plot_service,
)
from lightcurve_api.services.lightcurve_plot_service.service import get_periodogram_data
from lightcurve_api.services.lightcurve_plot_service.result import Result
from lightcurve_api.services.parsers import parse_ztf_dr_detection

from .parsers import (
    ConfigState,
)

router = APIRouter(prefix="/htmx")

templates = Jinja2Templates(
    directory="src/lightcurve_api/routes/htmx/templates",
    autoescape=True,
    auto_reload=True,
)

templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8001")


@router.get("/lightcurve", response_class=HTMLResponse)
def lightcurve(request: Request, oid: str, survey_id: str, db: db_dependency):
    """Return a self-contained HTML widget.

    All chart interactions (band toggles, magnitude/flux, fold, period, offsets)
    are handled entirely in the browser via lightcurve-app.js.  The server only
    provides the raw data as JSON embedded in the page.
    """
    result = lightcurve_plot_service.get_lightcurve_data(oid, survey_id, db.session)

    config_data = result.config_state.model_dump(exclude={"detections", "non_detections", "forced_photometry"})

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={
            "request": request,
            "detections": [d.model_dump() for d in result.lightcurve.detections],
            "non_detections": [d.model_dump() for d in result.lightcurve.non_detections],
            "forced_photometry": [d.model_dump() for d in result.lightcurve.forced_photometry],
            "periodogram": result.periodogram.model_dump(),
            "config": config_data,
        },
    )


@router.get("/periodogram", response_class=JSONResponse)
def periodogram(oid: str, survey_id: str, db: db_dependency):
    """Compute and return the periodogram for an object on demand.

    Called by lightcurve-app.js the first time the user enables fold mode.
    Keeping this out of the initial page-load request avoids the heavy
    Lomb-Scargle computation on every view.
    """
    pd = get_periodogram_data(oid, survey_id, db.session)
    return pd.model_dump()


@router.get("/external_sources", response_class=HTMLResponse)
def external_sources(request: Request, oid: str, survey_id: str, meanra: float = None, meandec: float = None):
    """Return an HTML picker of nearby ZTF DR objects for the external-sources feature."""
    config_state = ConfigState(
        oid=oid,
        survey_id=survey_id,
        meanra=meanra,
        meandec=meandec,
        external_sources={"enabled": True},
    )
    result = lightcurve_plot_service.get_ztf_dr_objects(
        config_state,
        [],
        [],
        [],
    )
    return templates.TemplateResponse(
        name="external_sources.html.jinja",
        context={"request": request, "config_state": result.config_state},
    )


@router.get("/dr_detections", response_class=JSONResponse)
def dr_detections(ra: float, dec: float, oids: str = ""):
    """Return ZTF DR detections as JSON for the given sky coordinates.

    Called by lightcurve-app.js when the user confirms an external-sources selection.
    ``oids`` is a comma-separated list of ZTF DR object IDs to include; if empty,
    all objects within the search radius are returned.
    """
    selected = [o.strip() for o in oids.split(",") if o.strip()] if oids else []
    with httpx.Client() as client:
        raw = client.get(
            "https://api.alerce.online/ztf/dr/v1/light_curve/",
            params={"ra": ra, "dec": dec, "radius": 1.5},
        ).json()
    detections = parse_ztf_dr_detection(raw, selected)
    return [d.model_dump() for d in detections]


@router.get("/download", response_class=HTMLResponse)
def download(oid: str, survey_id: str, db: db_dependency):
    """Download the lightcurve as a ZIP archive."""
    service_result = pipe(
        Result(
            {},
            Lightcurve(detections=[], non_detections=[], forced_photometry=[]),
            config_state=ConfigState(),
            periodogram=Periodogram(periods=[], scores=[], best_periods=[], best_periods_index=[]),
        ),
        curry(
            lightcurve_plot_service.get_lightcurve,
            oid=oid,
            survey_id=survey_id,
            session_factory=db.session,
        ),
    )
    zip_buffer = lightcurve_plot_service.zip_lightcurve(
        service_result.lightcurve.detections,
        service_result.lightcurve.non_detections,
        service_result.lightcurve.forced_photometry,
        int(oid),
    )

    day = str(date.today()).replace("-", "")
    filename_str = f"{oid}_{day}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename_str}"},
    )
