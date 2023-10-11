import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader, select_autoescape

from core.service import get_detections, get_non_detections
from database.mongo import database
from database.sql import session

from ..result_handler import handle_error, handle_success

router = APIRouter()
jinja_env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape(),
)

jinja_env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")


@router.get("/plot/difference")
def diff_plot(oid: str) -> HTMLResponse:
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

    detections = list(map(lambda det: det.__dict__, detections))
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))

    return HTMLResponse(
        jinja_env.get_template("difference.html.j2").render(
            detections=detections, non_detections=non_detections
        )
    )


@router.get("/plot/apparent")
def apparent_plot(oid: str) -> HTMLResponse:
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

    detections = list(map(lambda det: det.__dict__, detections))
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))

    return HTMLResponse(
        jinja_env.get_template("apparent.html.j2").render(

            detections=detections, non_detections=non_detections
        )
    )
