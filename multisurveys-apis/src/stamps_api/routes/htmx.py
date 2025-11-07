from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request, Response
from ..s3_handler import handler_selector
from ..services.lightcurve_service import get_detections
from ..models.lightcurve import LightcurveModel, detection
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
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8001")

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


###
# We need a get method that return all the stamps and get the 
# detections list from the db
# and a post method that comes with the detections list
# both return the same template
###



@router.get("/stamp_card")
async def get_stamp_card(
    request: Request,
    oid: str,
    survey_id: str,
    measurement_id: str | None = None,
    detections_list: LightcurveModel | None = None,
):
    handler = handler_selector(survey_id)()

    detections = get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=request.app.state.psql_session,
    )
    print("detections:")
    print(detections)
    measurement_id = detections[0].measurement_id

    stamps = handler.get_all_stamps(oid, measurement_id, "png")

    context = build_image_context(stamps)
    context.update({
        "request": request,
        "oid": oid,
        "detections": [d.to_json() for d in detections],
    })
    
    print(f"context: {context}")
    return templates.TemplateResponse(
      name='stamps_card.html.jinja',
      context=context,
    )


@router.post("/stamp_card")
async def post_stamp_card(
    request: Request,
    oid: str,
    measurement_id: str,
    survey_id: str,
    detections_list:LightcurveModel | None = None,
):
    handler = handler_selector(survey_id)()

    stamps = handler.get_all_stamps(oid, measurement_id, "png")

    context = build_image_context(stamps)
    context.update({
        "request": request,
        "oid": oid,
        "detections": [d.to_json() for d in detections_list.detections],
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
