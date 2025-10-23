import os
import pprint
from fastapi import FastAPI, Request
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/htmx")
templates = Jinja2Templates(
    directory="src/aladin_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8006"
)


@router.get("/aladin", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):

    objects_list = [{
        'oid': 'ZTF19abqshry',
        'meanra': '249.6383295266666',
        'meandec': '45.63117178'
    }]

    selected_object = {
        'oid': 'ZTF19abqshry',
        'meanra': '249.6383295266666',
        'meandec': '45.63117178'
    }

    return templates.TemplateResponse(
      name='layout.html.jinja',
      context={
            'request': request,
            'objects': objects_list,
            'selected_object': selected_object
        },
  )
