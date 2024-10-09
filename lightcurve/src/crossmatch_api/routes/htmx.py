
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
from ..get_crossmatch_data import get_alerce_data
router = APIRouter()
templates = Jinja2Templates(
    directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)

@router.get("/crossmatch/{oid}", response_class=HTMLResponse)
async def object_mag_app(
    request: Request,
    oid: str,
):
    
    object = get_object(oid,session_factory = request.app.state.psql_session)

    cross = get_alerce_data(object.meanra, object.meandec, 50)
    
    cross_keys_raw = []
    for i in range(len(cross)):
        cross_keys_raw.append(list(cross[i].keys())[0])

    cross_keys = []
    for i in range(len(cross)):
        if list(cross[i].values())[0]['distance']['value'] <= 20:
            cross_keys.append(list(cross[i].keys())[0])

    return templates.TemplateResponse(
      name='crossmatch.html.jinja',
      context={'request': request,
               'cross': cross,
               'crossKeys': cross_keys
               },
  )
