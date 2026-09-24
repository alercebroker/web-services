import os

from datetime import date

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from toolz import curry, pipe

from core.config.dependencies import db_dependency
from core.exceptions import ObjectNotFound
from core.idmapper.idmapper import catalog_oid_to_masterid
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.periodogram import NoPeriodError, Periodogram
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


def _validate_oid(oid: str, survey_id: str) -> int:
    """Return the master id for ``oid``, or answer 400 when it is not a valid id for the survey."""
    try:
        return catalog_oid_to_masterid(survey_id, oid, validate=True).item()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/lightcurve", response_class=HTMLResponse)
def lightcurve(request: Request, oid: str, survey_id: str, db: db_dependency):
    """Return a self-contained HTML widget.

    All chart interactions (band toggles, magnitude/flux, fold, period, offsets)
    are handled entirely in the browser via lightcurve-app.js.  The server only
    provides the raw data as JSON embedded in the page.
    """
    survey_id = survey_id.lower()
    _validate_oid(oid, survey_id)
    try:
        result = lightcurve_plot_service.get_lightcurve_data(oid, survey_id, db.session)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")

    config_data = result.config_state.model_dump(exclude={"detections", "non_detections", "forced_photometry"})

    detections = result.lightcurve.detections
    # "Total" (science) magnitude is only meaningful for corrected data. The server
    # decides this once, using the same model conversion the plot relies on, so the
    # browser doesn't need the raw photometry fields to make the call.
    not_corrected = detections[0].flux2magnitude(True, False) == 0 if detections else True

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={
            "request": request,
            "detections": [lightcurve_plot_service.detection_plot_record(d) for d in detections],
            "non_detections": [
                lightcurve_plot_service.non_detection_plot_record(d) for d in result.lightcurve.non_detections
            ],
            "forced_photometry": [
                lightcurve_plot_service.forced_photometry_plot_record(d) for d in result.lightcurve.forced_photometry
            ],
            "periodogram": result.periodogram.model_dump(),
            "config": config_data,
            "not_corrected": not_corrected,
        },
    )


@router.get("/periodogram", response_class=JSONResponse)
def periodogram(oid: str, survey_id: str, db: db_dependency):
    """Compute and return the periodogram for an object on demand.

    Called by lightcurve-app.js the first time the user enables fold mode.
    Keeping this out of the initial page-load request avoids the heavy
    Lomb-Scargle computation on every view.
    """
    survey_id = survey_id.lower()
    _validate_oid(oid, survey_id)
    try:
        pd = get_periodogram_data(oid, survey_id, db.session)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")
    payload = pd.model_dump()
    try:
        payload["best_candidate_period"] = pd.get_best_candidate_period()
    except NoPeriodError:
        payload["best_candidate_period"] = None
    return payload


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
    return [lightcurve_plot_service.detection_plot_record(d) for d in detections]


@router.get(
    "/download",
    response_class=Response,
    responses={200: {"content": {"application/zip": {}}, "description": "The lightcurve as a ZIP of CSV files."}},
)
def download(oid: str, survey_id: str, db: db_dependency):
    """Download the lightcurve as a ZIP archive.

    ``oid`` is the survey's own id (the ZTF name, or the numeric LSST id). The rows
    are matched on the internal master id, but the file name and the CSVs keep the
    id the caller sent.
    """
    survey_id = survey_id.lower()
    master_id = _validate_oid(oid, survey_id)

    try:
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
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")

    zip_buffer = lightcurve_plot_service.zip_lightcurve(
        service_result.lightcurve.detections,
        service_result.lightcurve.non_detections,
        service_result.lightcurve.forced_photometry,
        master_id=master_id,
        catalog_oid=oid,
        survey_id=survey_id,
    )

    day = str(date.today()).replace("-", "")
    filename_str = f"{oid}_{day}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename_str}"},
    )
