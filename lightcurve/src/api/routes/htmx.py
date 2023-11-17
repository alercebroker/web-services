import os

from data.load import get_dummy_features, get_dummy_lc
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader, select_autoescape

from core.service import (
    get_data_release,
    get_detections,
    get_non_detections,
    get_period,
)
from database.mongo import database
from database.sql import session

from ..result_handler import handle_error, handle_success

router = APIRouter()
jinja_env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape(),
)

jinja_env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")


@router.get("/lightcurve")
async def lightcurve(oid: str) -> HTMLResponse:
    #detections = get_detections(
    #    oid=oid,
    #    survey_id="ztf",
    #    session_factory=session,
    #    mongo_db=database,
    #    handle_error=handle_error,
    #    handle_success=handle_success,
    #)

    #non_detections = get_non_detections(
    #    oid=oid,
    #    survey_id="ztf",
    #    session_factory=session,
    #    mongo_db=database,
    #    handle_error=handle_error,
    #    handle_success=handle_success,
    #)

    #period = get_period(
    #    oid=oid,
    #    survey_id="ztf",
    #    session_factory=session,
    #    mongo_db=database,
    #    handle_error=handle_error,
    #    handle_success=handle_success,
    #)
    detections, non_detections = get_dummy_lc()
    features = get_dummy_features()
    period = list(
        filter(lambda feat: feat.name == "Multiband_period", features)
    )[0]

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

    return HTMLResponse(
        jinja_env.get_template("lightcurve.html.j2").render(
            oid=oid,
            detections=detections,
            non_detections=non_detections,
            period=period,
            dr=dr,
            dr_detections=dr_detections,
        )
    )
