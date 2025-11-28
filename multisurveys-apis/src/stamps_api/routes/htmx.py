from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request, Response
from ..s3_handler import handler_selector
from ..services.lightcurve_service import get_detections
from ..models.lightcurve import LightcurveModel, detection, PostRequestInputModel
from fastapi.templating import Jinja2Templates
from astropy.time import Time
import os
import base64

router = APIRouter()

templates = Jinja2Templates(
    directory="src/stamps_api/templates",
    autoescape=True,
    auto_reload=True,
)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8007")

"""
Service
    - get lightcurve ordered by date dect
    - get stamps for oid and measurement id

Functions
    - get (no measurement_id no detections list) 
        Get the lightcurve and de stamps for the fist measurement id
        in the list of detections
    - post (with measurement_id with detections list)
        Get the stamps for the oid and measruement id
difference_mime
    bot return the template whith whe
    lightcurve and stamps
"""


@router.get("/stamp_card")
async def get_stamp_card(
    request: Request,
    oid: str,
    survey_id: str,
):
    handler = handler_selector(survey_id)()

    detections = get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=request.app.state.psql_session,
    )
    selected_measurement_id = detections[0].measurement_id
    next_measurement_id = detections[min(1, len(detections) - 1)].measurement_id

    stamps = handler.get_all_stamps(oid, selected_measurement_id, "png")
    context = build_image_context(stamps)
    context.update({
        "request": request,
        "oid": oid,
        "survey_id": survey_id,
        "detections": [d.to_json() for d in detections],
        "selected_measurement_id": str(selected_measurement_id),
        "prv_measurement_id": str(selected_measurement_id),
        "nxt_measurement_id": str(next_measurement_id),
    })
    
    return templates.TemplateResponse(
      name='stamps_layout.html.jinja',
      context=context,
    )


@router.post("/update_stamp_card")
async def post_stamp_card(
    request: Request,
    post_input: PostRequestInputModel
):
    handler = handler_selector(post_input.survey_id)()

    stamps = handler.get_all_stamps(post_input.oid, post_input.measurement_id, "png")

    prv_measurement_id, nxt_measurement_id = find_prv_and_nxt_measurement_ids(
        post_input.detections_list,
        selected_measurement_id=post_input.measurement_id,
    )

    context = build_image_context(stamps)
    context.update({
        "request": request,
        "oid": post_input.oid,
        "survey_id": post_input.survey_id,
        "detections": post_input.detections_list,
        "selected_measurement_id": str(post_input.measurement_id),
        "prv_measurement_id": str(prv_measurement_id),
        "nxt_measurement_id": str(nxt_measurement_id),
    })

    return templates.TemplateResponse(
      name='stamps_card.html.jinja',
      context=context,
    )

def build_image_context(stamps: dict) -> dict:
    return {
        "science_mime": stamps['cutoutScience']['mime'],
        "science_img": base64.b64encode(stamps['cutoutScience']['file']).decode("utf-8"),
        "template_mime": stamps['cutoutTemplate']['mime'],
        "template_img": base64.b64encode(stamps['cutoutTemplate']['file']).decode("utf-8"),
        "difference_mime": stamps['cutoutDifference']['mime'],
        "difference_img": base64.b64encode(stamps['cutoutDifference']['file']).decode("utf-8"),
    }

def find_prv_and_nxt_measurement_ids(detections: list[dict], selected_measurement_id: int) -> tuple[int | None, int | None]:
    prv_id = selected_measurement_id
    nxt_id = selected_measurement_id
    for idx, det in enumerate(detections):
        if det["measurement_id"] == str(selected_measurement_id):
            if idx > 0:
                prv_id = detections[idx - 1]["measurement_id"]
            if idx < len(detections) - 1:
                nxt_id = detections[idx + 1]["measurement_id"]
            break
    return prv_id, nxt_id