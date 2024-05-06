import re
import os
from typing import Annotated
from fastapi import Query

from core.service import (
    get_data_release,
    get_detections,
    get_non_detections,
    get_period,
    get_forced_photometry,
    query_psql_object,
    remove_duplicate_forced_photometry_by_pid
)
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)


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


def get_detections_as_dict(oid, survey_id, psql_session, mongo_database):
    detections = get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=psql_session,
        mongo_db=mongo_database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    if detections is not None:
        detections = list(map(lambda det: det.__dict__, detections))
        return detections


def get_non_detections_as_dict(oid, survey_id, psql_session, mongo_database):
    non_detections = get_non_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=psql_session,
        mongo_db=mongo_database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    if non_detections is not None:
        non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
        return non_detections


def get_period_value(oid, psql_session):
    period = get_period(
        oid=oid,
        survey_id="ztf",
        session_factory=psql_session,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    if period:
        return period.value


def get_forced_photometry_as_dict(oid, psql_session, mongo_database):
    forced_photometry = get_forced_photometry(
        oid=oid,
        survey_id="ztf",
        session_factory=psql_session,
        mongo_db=mongo_database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
    if forced_photometry is not None:
        forced_photometry = list(map(lambda fp: fp.__dict__, forced_photometry))
        return forced_photometry


async def get_data_release_as_dict(oid, psql_session, dr_ids: list[str] = []):
    """Get data release detections for a given object and optionally filter by data release ids.

    Args:
        oid (str): Object id.
        dr_ids (list[str], optional): Data release ids. Defaults to [].

    Returns:
        tuple: Data release object data and detections.

    """
    obj = query_psql_object(oid, psql_session)
    dr, dr_detections = await get_data_release(obj.meanra, obj.meandec)
    dr_detections = {str(k): v for k, v in dr_detections.items()}
    if len(dr_ids) == 0:
        result = {}
        for dr_id in dr_detections:
            result[dr_id] = list(map(lambda det: det.__dict__, dr_detections[dr_id]))
        return dr, result
    elif "none" in dr_ids:
        return dr, {}
    else:
        result = {}
        for dr_id in dr_ids:
            result[dr_id] = list(map(lambda det: det.__dict__, dr_detections[dr_id]))
        return dr, result


async def get_lightcurve(oid, survey_id, psql_session, mongo_database):
    detections = get_detections_as_dict(oid, survey_id, psql_session, mongo_database)
    non_detections = get_non_detections_as_dict(oid, survey_id, psql_session, mongo_database)
    forced_photometry = get_forced_photometry_as_dict(oid, psql_session, mongo_database)
    if forced_photometry and detections:
        forced_photometry = remove_duplicate_forced_photometry_by_pid(
            detections, forced_photometry
        )
    return {
        "detections": detections,
        "non_detections": non_detections,
        "forced_photometry": forced_photometry,
    }

def filter_atlas_lightcurve(lightcurve: dict, ralidator):
    ralidator.set_app_filters(["filter_atlas_lightcurve"])
    return ralidator.apply_filters(lightcurve)


async def get_data_and_filter(
    request: Request, oid: str, survey_id: str = "all"
):
    setup_ralidator(request)
    unfiltered_lightcurve = await get_lightcurve(oid, survey_id, request.app.state.psql_session, request.app.state.mongo_db)
    filtered_lightcurve = filter_atlas_lightcurve(
        unfiltered_lightcurve, request.state.ralidator
    )
    return filtered_lightcurve


@router.get("/lightcurve", response_class=HTMLResponse)
async def lightcurve_app(
    request: Request,
    oid: str,
    survey_id: str = "all",
    plot_type: str = "difference",
    dr_ids: Annotated[list[str], Query()] = [],
    show_dr: bool = False,
):
    lightcurve = await get_data_and_filter(request, oid, survey_id)
    return templates.TemplateResponse(
        name="lightcurve_app.html.jinja",
        context={
            "request": request,
            "oid": oid,
            "lightcurve": lightcurve,
            "plot_type": plot_type,
            "dr_detections": [],
            "period": 0,
            "dr_ids": dr_ids,
            "dr": [],
            "show_dr": show_dr
        },
    )

@router.get("/lightcurve_dr", response_class=HTMLResponse)
async def lightcurve_app(
    request: Request,
    oid: str,
    survey_id: str = "all",
    plot_type: str = "difference",
    dr_ids: Annotated[list[str], Query()] = [],
    show_dr: bool = False,
):
    dr, dr_detections = await get_data_release_as_dict(oid, request.app.state.psql_session, dr_ids)
    period = get_period_value(oid, request.app.state.psql_session)
    return templates.TemplateResponse(
        name="lightcurve_app.html.jinja",
        context={
            "request": request,
            "oid": oid,
            #"lightcurve": lightcurve,
            "plot_type": plot_type,
            "dr_detections": dr_detections,
            "period": period,
            "dr_ids": dr_ids,
            "dr": dr,
            "show_dr": show_dr
        },
    )


@router.get("/lightcurve/dr", response_class=HTMLResponse)
async def dr(
    request: Request, oid: str, dr_ids: Annotated[list[str], Query()] = []
):
    dr, dr_detections = await get_data_release_as_dict(oid, request.app.state.psql_session, dr_ids)
    return templates.TemplateResponse(
        name="data_release_table.html.jinja",
        context={
            "request": request,
            "oid": oid,
            "dr": dr,
            "dr_detections": dr_detections,
            "selected": dr_ids,
        },
    )
