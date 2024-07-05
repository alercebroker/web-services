import re
import os
from typing import Annotated
from fastapi import Query
import json

#from core.services.object import get_mag_stats
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/banner_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8006"
)

@router.get("/banner", response_class=HTMLResponse)
async def object_banner_app(
    request: Request,
):

    return templates.TemplateResponse(
      name='banner.html.jinja',
      context={'request': request,
               },
  )

