import re
import os
from typing import Annotated
from fastapi import Query
import json

from core.services.object import get_object
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["OAPI_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8001"
)

@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(
    request: Request,
    oid: str
):
  
    link='https://acortar.link/ba5kba'
    

    object = get_object(oid,session_factory = request.app.state.psql_session)

    return {
        'request': request,
        'object': object.oid,
        'corrected': object.corrected,
        'stellar' : object.stellar,
        'detections' : object.ndet,
        'discoveryDateMJD' : object.firstmjd,
        'lastDetectionMJD' : object.lastmjd,
        'ra' : object.meanra ,
        'dec': object.meandec,
        'link':link
    }

