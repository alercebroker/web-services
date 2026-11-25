import logging
from datetime import date

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from toolz import curry, pipe

from core.config.dependencies import db_dependency
from core.idmapper.idmapper import parse_oid, public_oid
from core.idmapper.survey_mapper import Survey
from core.static_files import configure_templates, html_templates
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.periodogram import NoPeriodError, Periodogram
from lightcurve_api.services.lightcurve_plot_service import (
    service as lightcurve_plot_service,
)
from lightcurve_api.services import group_service
from lightcurve_api.services.lightcurve_plot_service.result import Result
from lightcurve_api.services.lightcurve_plot_service.service import get_periodogram_data
from lightcurve_api.services.parsers import parse_ztf_dr_detection

from .parsers import (
    ConfigState,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/htmx")

templates = html_templates("src/lightcurve_api/routes/htmx/templates")

configure_templates(templates, "http://localhost:8001")


@router.get("/lightcurve", response_class=HTMLResponse)
def lightcurve(request: Request, oid: str, survey_id: Survey, db: db_dependency):
    """Return a self-contained HTML widget.

    All chart interactions (band toggles, magnitude/flux, fold, period, offsets)
    are handled entirely in the browser via lightcurve-app.js.  The server only
    provides the raw data as JSON embedded in the page.
    """
    parse_oid(survey_id, oid)
    result = lightcurve_plot_service.get_lightcurve_data(oid, survey_id, db.session)

    config_data = result.config_state.model_dump(exclude={"detections", "non_detections", "forced_photometry"})

    detections = result.lightcurve.detections
    # "Total" (science) magnitude is only meaningful for corrected data. The server
    # decides this once, using the same model check the plot relies on, so the
    # browser doesn't need the raw photometry fields to make the call. An object is
    # only "not corrected" when none of its detections are: mixed objects show the
    # corrected ones.
    not_corrected = not any(d.has_total() for d in detections)

    return templates.TemplateResponse(
        request=request,
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
            # Chart title: the ZTF name, also when the URL has the numeric id
            "object_name": public_oid(survey_id, oid),
            "group": _group_info(oid, survey_id, db.session),
        },
    )


def _group_info(oid: str, survey_id: str, session_factory) -> dict | None:
    """The object's group for the members panel, or None where groups aren't available.

    The association tables are still a test schema, so a failure here only hides the panel: the object's own
    light curve is shown either way.
    """
    if not group_service.association_enabled():
        return None
    try:
        info = group_service.get_group_info(oid, survey_id, session_factory)
    except Exception:
        logger.warning("Could not read the group of %s %s", survey_id, oid, exc_info=True)
        return None
    return info.to_dict() if info else None


@router.get("/group_photometry", response_class=JSONResponse)
def group_photometry(objects: str, db: db_dependency):
    """Detections and forced photometry of other objects, for the group panel of the light curve.

    ``objects`` is a comma-separated list of ``<survey>:<oid>`` (``ztf:ZTF19aaxlmra,lsst:313853798223069211``),
    at most 20. Each record carries ``oid``, the object it belongs to. Called by lightcurve-app.js for the
    members shown by default and for each nearby object the user turns on.
    """
    return group_service.get_group_photometry(objects, db.session)


@router.get("/periodogram", response_class=JSONResponse)
def periodogram(oid: str, survey_id: Survey, db: db_dependency):
    """Compute and return the periodogram for an object on demand.

    Called by lightcurve-app.js the first time the user enables fold mode.
    Keeping this out of the initial page-load request avoids the heavy
    Lomb-Scargle computation on every view.
    """
    parse_oid(survey_id, oid)
    pd = get_periodogram_data(oid, survey_id, db.session)
    payload = pd.model_dump()
    try:
        payload["best_candidate_period"] = pd.get_best_candidate_period()
    except NoPeriodError:
        payload["best_candidate_period"] = None
    return payload


@router.get("/external_sources", response_class=HTMLResponse)
def external_sources(request: Request, oid: str, survey_id: Survey, meanra: float = None, meandec: float = None):
    """Return an HTML picker of nearby ZTF DR objects for the external-sources feature."""
    if meanra is None or meandec is None:
        raise ValueError("meanra and meandec are required")  # answered as 400 by the central handler
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
        request=request,
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
def download(oid: str, survey_id: Survey, db: db_dependency):
    """Download the lightcurve as a ZIP archive.

    ``oid`` is the survey's own id (the ZTF name, or the numeric LSST id). The rows
    are matched on the internal master id, but the file name and the CSVs keep the
    id the caller sent.
    """
    master_id = parse_oid(survey_id, oid)

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
