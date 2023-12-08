import os
import re

from core.service import (
    get_data_release,
    get_detections,
    get_non_detections,
    get_period,
)
from database.mongo import database
from database.sql import session
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader, select_autoescape
from ralidator_fastapi.decorators import (
    check_permissions_decorator,
    set_filters_decorator,
    set_permissions_decorator,
)
from ..result_handler import handle_error, handle_success

router = APIRouter()
jinja_env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape(),
)

jinja_env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")


@router.get("/lightcurve")
async def lightcurve(
    request: Request,
    oid: str
) -> HTMLResponse:
    # el objeto ralidator viene en request.state
    request_ralidator = request.state.ralidator

    # permissions logic
    request_ralidator.set_required_permissions(
        "admin", "basic_user"
    )
    auth_header = request.headers.get("Authorization")
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
        survey_id="ztf",
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    non_detections = get_non_detections(
        oid=oid,
        survey_id="ztf",
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

    dr, dr_detections = await get_data_release(
        detections[0].ra, detections[0].dec
    )

    detections = list(map(lambda det: det.__dict__, detections))
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
    period = period.value
    dr_detections = {
        k: list(map(lambda det: det.__dict__, detections))
        for k, detections in dr_detections.items()
    }

    # crear objeto de lightcurve
    unfiltered_lightcurve = {
        "detections": detections,
        "non_detections": non_detections
    }
    # editar el ralidator para ejecutar filtro de lightcurveset_user_filters con "filter lightcurve altas"
    request_ralidator.set_app_filters(
        ["filter_atlas_lightcurve"]
    )
    # ejecutar apply_filters
    filtered_lightcurve = request_ralidator.apply_filters(
        unfiltered_lightcurve
    )

    # sacar detections y non detections del lightcurve filtrado
    return HTMLResponse(
        jinja_env.get_template("lightcurve.html.j2").render(
            oid=oid,
            detections=filtered_lightcurve["detections"],
            non_detections=filtered_lightcurve["non_detections"],
            period=period,
            dr=dr,
            dr_detections=dr_detections,
        )
    )
