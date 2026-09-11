import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..services.crossmatch_service import get_cross_for_frontend
from ..models.object import ObjectInformation


router = APIRouter()
templates = Jinja2Templates(directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8005")


@router.get("/htmx/crossmatch", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str, survey_id: str):
    session = request.app.state.psql_session

    object_details = ObjectInformation(oid=oid, survey=survey_id)

    cross, cross_keys = get_cross_for_frontend(object_details, session)


    return templates.TemplateResponse(
        name="crossmatch.html.jinja",
        context={
            "request": request,
            "cross": cross,
            "crossKeys": cross_keys,
        },
    )

