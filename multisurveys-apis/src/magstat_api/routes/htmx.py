import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
from core.repository.queries.magstats import get_magstats_by_oid
from core.repository.dummy_data import magstats_dummy


router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath("src/magstat_api/templates"), autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8002"
)


@router.get("/htmx/mag", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str):
    return templates.TemplateResponse(
        name="magstatRebuild.html.jinja",
        context={"request": request, "stat_r": magstats_dummy},
    )
