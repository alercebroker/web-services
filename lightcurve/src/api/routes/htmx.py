import re
import os

from core.service import (
    get_data_release,
    get_detections,
    get_non_detections,
    get_period,
    get_forced_photometry,
)
from database.mongo import database
from database.sql import session
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success
from ..plots import difference as plot_diff
from ..plots import apparent as plot_ap

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")

def setup_ralidator(request: Request):
    # el objeto ralidator viene en request.state
    request_ralidator = request.state.ralidator
    # permissions logic
    request_ralidator.set_required_permissions(["admin", "basic_user"])
    auth_header = request.headers.get("Authorization", None)
    token = None
    if auth_header:
        if re.search("bearer", auth_header, re.IGNORECASE) is None:
            raise ValueError("Malformed Authorization header")
        try:
            token = auth_header.split()[1]
        except Exception:
            raise ValueError("Malformed Authorization header")
    request_ralidator.authenticate_token(token)
    allowed, code = request_ralidator.check_if_allowed()
    if not allowed:
        if code == 401:
            raise HTTPException(status_code=code, detail="Expired Token")
        raise HTTPException(status_code=code, detail="Unauthorized")

def get_detections_as_dict(oid, survey_id):
    detections = get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    detections = list(map(lambda det: det.__dict__, detections))
    return detections

def get_non_detections_as_dict(oid, survey_id):
    non_detections = get_non_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
    return non_detections

def get_period_value(oid):
    period = get_period(
        oid=oid,
        survey_id="ztf",
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    return period.value

def get_forced_photometry_as_dict(oid):
    forced_photometry = get_forced_photometry(
        oid=oid,
        survey_id="ztf",
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    forced_photometry = list(map(lambda fp: fp.__dict__, forced_photometry))
    return forced_photometry

async def get_data_release_as_dict(detections):
    dr, dr_detections = await get_data_release(
        detections[0]["ra"], detections[0]["dec"]
    )
    dr_detections = {
        k: list(map(lambda det: det.__dict__, detections))
        for k, detections in dr_detections.items()
    }
    return dr, dr_detections

async def get_lightcurve(oid, survey_id):
    detections = get_detections_as_dict(oid, survey_id)
    non_detections = get_non_detections_as_dict(oid, survey_id)
    forced_photometry = get_forced_photometry_as_dict(oid)
    period = get_period_value(oid)
    dr, dr_detections = await get_data_release_as_dict(detections)
    return {
        "detections": detections,
        "non_detections": non_detections,
        "forced_photometry": forced_photometry,
        "period": period,
        "data_release": dr,
        "dr_detections": dr_detections,
    }

def filter_atlas_lightcurve(lightcurve: dict, ralidator):
    ralidator.set_app_filters(["filter_atlas_lightcurve"])
    return ralidator.apply_filters(lightcurve)


async def get_data_and_filter(request: Request, oid: str, survey_id: str = "all"):
    setup_ralidator(request)
    unfiltered_lightcurve = await get_lightcurve(oid, survey_id)
    filtered_lightcurve = filter_atlas_lightcurve(unfiltered_lightcurve, request.state.ralidator)
    return filtered_lightcurve

@router.get("/lightcurve", response_class=HTMLResponse)
async def lightcurve(
    request: Request, oid: str, survey_id: str = "all"
) -> HTMLResponse:
    filtered_lightcurve = await get_data_and_filter(request, oid, survey_id)
    difference_options = plot_diff.difference_lightcurve_options(
        filtered_lightcurve["detections"],
        filtered_lightcurve["non_detections"],
        filtered_lightcurve["forced_photometry"],
        "#000",
        request.state.ralidator,
    )
    apparent_options = plot_ap.apparent_lightcurve_options(
        filtered_lightcurve["detections"],
        filtered_lightcurve["forced_photometry"],
        "#000",
        request.state.ralidator,
    )
    return templates.TemplateResponse(
        name="main.html.jinja",
        context={
            "plot_diff": difference_options,
            "plot_ap": apparent_options,
            "request": request,
            "oid": oid,
            "detections": filtered_lightcurve["detections"],
            "non_detections": filtered_lightcurve["non_detections"],
            "forced_photometry": filtered_lightcurve["forced_photometry"],
            "period": filtered_lightcurve["period"],
            "dr": filtered_lightcurve["data_release"],
            "dr_detections": filtered_lightcurve["dr_detections"],
        },
    )
