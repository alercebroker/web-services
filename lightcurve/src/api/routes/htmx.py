import re

from core.service import (
    get_data_release,
    get_detections,
    get_non_detections,
    get_period,
    get_forced_photometry,
)
from database.mongo import database
from database.sql import session
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates", autoescape=True, auto_reload=True)

@router.get("/lightcurve", response_class=HTMLResponse)
async def lightcurve(
    request: Request, oid: str, survey_id: str = "all"
) -> HTMLResponse:
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
        # TODO: fix error handling here
        if code == 401:
            return "Expired Token", code
        else:
            return "Forbidden", code

    # data logic
    detections = get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    non_detections = get_non_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    period = get_period(
        oid=oid,
        survey_id="ztf",
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    forced_photometry = get_forced_photometry(
        oid=oid,
        survey_id="ztf",
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    dr, dr_detections = await get_data_release(
        detections[0].ra, detections[0].dec
    )
    detections = list(map(lambda det: det.__dict__, detections))
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
    forced_photometry = list(map(lambda fp: fp.__dict__, forced_photometry))
    period = period.value
    dr_detections = {
        k: list(map(lambda det: det.__dict__, detections))
        for k, detections in dr_detections.items()
    }

    # crear objeto de lightcurve
    unfiltered_lightcurve = {
        "detections": detections,
        "non_detections": non_detections,
        "forced_photometry": forced_photometry,
    }
    # editar el ralidator para ejecutar filtro de lightcurveset_user_filters con "filter lightcurve altas"
    request_ralidator.set_app_filters(["filter_atlas_lightcurve"])
    # ejecutar apply_filters
    filtered_lightcurve = request_ralidator.apply_filters(
        unfiltered_lightcurve
    )

    # sacar detections y non detections del lightcurve filtrado
    return templates.TemplateResponse(
        name="lightcurve.html.j2",
        context={
            "request": request,
            "oid": oid,
            "detections": filtered_lightcurve["detections"],
            "non_detections": filtered_lightcurve["non_detections"],
            "forced_photometry": forced_photometry,
            "period": period,
            "dr": dr,
            "dr_detections": dr_detections,
        },
    )
