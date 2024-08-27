import re
import os
from typing import Annotated
from fastapi import Query
import json

from core.services.object import get_mag_stats
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["OAPI_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8000"
)

@router.get("/mag/{oid}", response_class=HTMLResponse)
async def object_mag_app(
    request: Request,
    oid: str
):
  
    mag_stats = get_mag_stats(oid,session_factory = request.app.state.psql_session)
    mag_stats_dict = {}
    for n in range(len(mag_stats)):
        mag_stats_dict[f"band_{n+1}"] = mag_stats[n].__dict__ ## Es necesario cambiar el nombre de las keys por los fid y trabajar con el conversor que esta en probability en alerts-api

    return { 
        'request': request,
        'stat_r': mag_stats_dict
    }
