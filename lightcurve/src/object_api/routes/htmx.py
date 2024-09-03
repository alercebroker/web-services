import re
import os
from typing import Annotated
from fastapi import Query
import json

from core.services.object import get_object,get_first_det_candid, get_count_ndet
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)

@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(
    request: Request,
    oid: str
):

    object = get_object(oid,session_factory = request.app.state.psql_session)
    candid = get_first_det_candid(oid, object.firstmjd, session_factory = request.app.state.psql_session)
    count_ndet = get_count_ndet(oid,session_factory = request.app.state.psql_session)
    

    return templates.TemplateResponse(
      name='basicInformationPreview.html.jinja',
      context={
                'request': request,
                'object': object.oid,
                'corrected': "Yes" if object.corrected else "No",
                'stellar' : "Yes" if object.stellar else "No",
                'detections' : object.ndet,
                'nonDetections' : count_ndet,
                'discoveryDateMJD' : object.firstmjd,
                'lastDetectionMJD' : object.lastmjd,
                'ra' : object.meanra ,
                'dec': object.meandec,
                'candid': candid
            },
  )
