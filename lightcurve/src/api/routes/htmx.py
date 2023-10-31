import os

import httpx
from data.load import get_dummy_features, get_dummy_lc
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader, select_autoescape

from core.models import Detection
from core.service import get_detections, get_non_detections, get_period
from database.mongo import database
from database.sql import session

from ..result_handler import handle_error, handle_success

router = APIRouter()
jinja_env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape(),
)

jinja_env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")


# @router.get("/plot/difference")
# def diff_plot(oid: str) -> HTMLResponse:
#     detections = get_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     non_detections = get_non_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     detections, non_detections = get_dummy_lc()

#     detections = list(map(lambda det: det.__dict__, detections))
#     non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))

#     return HTMLResponse(
#         jinja_env.get_template("difference.html.j2").render(
#             detections=detections, non_detections=non_detections
#         )
#     )


# @router.get("/plot/apparent")
# def apparent_plot(oid: str) -> HTMLResponse:
#     detections = get_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     non_detections = get_non_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     detections = list(map(lambda det: det.__dict__, detections))
#     non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))

#     return HTMLResponse(
#         jinja_env.get_template("apparent.html.j2").render(
#             detections=detections, non_detections=non_detections
#         )
#     )


# @router.get("/plot/folded")
# def folded_plot(oid: str) -> HTMLResponse:
#     detections = get_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     non_detections = get_non_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     period = get_period(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     detections = list(map(lambda det: det.__dict__, detections))
#     non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
#     period = period.value

#     return HTMLResponse(
#         jinja_env.get_template("folded.html.j2").render(
#             detections=detections, non_detections=non_detections, period=period
#         )
#     )


# @router.get("/button/download")
# def download_button(oid: str) -> HTMLResponse:
#     detections = get_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     non_detections = get_non_detections(
#         oid=oid,
#         survey_id="ztf",
#         session_factory=session,
#         mongo_db=database,
#         handle_error=handle_error,
#         handle_success=handle_success,
#     )

#     detections = list(map(lambda det: det.__dict__, detections))
#     non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))

#     return HTMLResponse(
#         jinja_env.get_template("download_lc.html.j2").render(
#             oid=oid, detections=detections, non_detections=non_detections
#         )
#     )


@router.get("/lightcurve")
def lightcurve(oid: str) -> HTMLResponse:
    # detections = get_detections(
    #     oid=oid,
    #     survey_id="ztf",
    #     session_factory=session,
    #     mongo_db=database,
    #     handle_error=handle_error,
    #     handle_success=handle_success,
    # )

    # non_detections = get_non_detections(
    #     oid=oid,
    #     survey_id="ztf",
    #     session_factory=session,
    #     mongo_db=database,
    #     handle_error=handle_error,
    #     handle_success=handle_success,
    # )

    # period = get_period(
    #     oid=oid,
    #     survey_id="ztf",
    #     session_factory=session,
    #     mongo_db=database,
    #     handle_error=handle_error,
    #     handle_success=handle_success,
    # )

    detections, non_detections = get_dummy_lc()
    features = get_dummy_features()
    period = list(
        filter(lambda feat: feat.name == "Multiband_period", features)
    )[0]

    dr_params = {
        "ra": detections[0].ra,
        "dec": detections[0].dec,
        "radius": "1.5",
    }
    dr_response = httpx.get(
        "https://api.alerce.online/ztf/dr/v1/light_curve/",
        params=dr_params,
        follow_redirects=True,
    )

    dr = [
        {
            k: dr_data[k]
            for k in ("_id", "filterid", "nepochs", "fieldid", "rcid")
        }
        for dr_data in dr_response.json()
    ]

    for datarelease in dr:
        datarelease["checked"] = False

    dr_detections = {
        dr_data["_id"]: [
            {
                "mjd": dr_data["hmjd"][i],
                "mag_corr": dr_data["mag"][i],
                "e_mag_corr_ext": dr_data["magerr"][i],
                "fid": dr_data["filterid"] + 100,
                "field": dr_data["fieldid"],
                "objectid": dr_data["_id"],
                "corrected": True,
            }
            for i in range(dr_data["nepochs"])
        ]
        for dr_data in dr_response.json()
    }

    detections = list(map(lambda det: det.__dict__, detections))
    non_detections = list(map(lambda ndet: ndet.__dict__, non_detections))
    period = period.value

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
