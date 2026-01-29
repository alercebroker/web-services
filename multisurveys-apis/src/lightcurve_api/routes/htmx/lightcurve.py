import os
import pprint

from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from toolz import curry, pipe

from core.config.dependencies import db_dependency
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.periodogram import Periodogram
from lightcurve_api.services.lightcurve_plot_service import (
    service as lightcurve_plot_service,
)
from lightcurve_api.services.lightcurve_plot_service.result import Result
from lightcurve_api.services.period.service import get_periodogram_chart

from .parsers import (
    ConfigState,
    parse_detections,
    parse_forced_photometry,
    parse_non_detections,
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
    result = lightcurve_plot_service.lightcurve_plot(oid, survey_id, db.session)
    result.config_state.oid = oid
    result.config_state.survey_id = survey_id

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={
            "request": request,
            "options": result.echart_options,
            "config_state": result.config_state,
            "detections": result.lightcurve.detections,
            "non_detections": result.lightcurve.non_detections,
            "forced_photometry": result.lightcurve.forced_photometry,
            "periodogram": result.periodogram,
            "periodogram_options": get_periodogram_chart(result.periodogram),
            "use_absolute": os.getenv("USE_ABSOLUTE", "false").lower() == "true",
        },
    )


@router.post("/config_change", response_class=HTMLResponse)
def config_change(request: Request, config_state: ConfigState):
    result = lightcurve_plot_service.update_lightcurve_plot(
        config_state,
        parse_detections(config_state.detections),
        parse_non_detections(config_state.non_detections),
        parse_forced_photometry(config_state.forced_photometry),
    )
    return templates.TemplateResponse(
        name="main.html.jinja",
        context={
            "request": request,
            "options": result.echart_options,
            "config_state": result.config_state,
            "detections": result.lightcurve.detections,
            "non_detections": result.lightcurve.non_detections,
            "forced_photometry": result.lightcurve.forced_photometry,
            "periodogram": result.periodogram,
            "periodogram_options": get_periodogram_chart(result.periodogram),
            "use_absolute": os.getenv("USE_ABSOLUTE", "false").lower() == "true",
        },
    )


@router.post("/external_sources", response_class=HTMLResponse)
def external_sources(request: Request, config_state: ConfigState):
    result = lightcurve_plot_service.get_ztf_dr_objects(
        config_state,
        parse_detections(config_state.detections),
        parse_non_detections(config_state.non_detections),
        parse_forced_photometry(config_state.forced_photometry),
    )
    return templates.TemplateResponse(
        name="external_sources.html.jinja",
        context={"request": request, "config_state": result.config_state},
    )


@router.get("/download", response_class=HTMLResponse)
def download(oid: str, survey_id: str, db: db_dependency):
    """Downloads the lightcurve"""
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
        int(oid)
    )

    day = str(date.today())
    day = day.replace('-', '')

    filename_str = oid + '_' + str(day) + '.zip' 

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename_str}",
        },
    )
