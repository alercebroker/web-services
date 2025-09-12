import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lightcurve_api.services.lightcurve_plot_service import service as lightcurve_plot_service
from core.config.dependencies import db_dependency
from .parsers import ConfigState, parse_detections, parse_non_detections, parse_forced_photometry


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
    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={
            "request": request,
            "options": result.echart_options,
            "config_state": result.config_state,
            "detections": result.lightcurve.detections,
            "non_detections": result.lightcurve.non_detections,
            "forced_photometry": result.lightcurve.forced_photometry,
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
