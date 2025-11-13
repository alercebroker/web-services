import os
from typing import List, Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..services.aladin_services import get_object_by_id
from ..services.aladin_parser import loads_objects_list

router = APIRouter(prefix="/htmx")
templates = Jinja2Templates(directory="src/aladin_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8006")


@router.post("/aladin", response_class=HTMLResponse)
async def object_probability_app(request: Request, oid: str, objects_arr: Optional[List[str]] = Form(None)):
    session_ms = request.app.state.psql_session

    objects_list = loads_objects_list(objects_arr)
    survey = ""
    selected_object = get_object_by_id(session_ms, oid, survey)

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={"request": request, "objects": objects_list, "selected_object": selected_object},
    )


@router.get("/aladin", response_class=HTMLResponse)
async def object_probability_app_get(
    request: Request,
    oid: Optional[str] = None,
    objects_arr: Optional[List[str]] = Query(None),
):
    session_ms = request.app.state.psql_session

    objects_list = loads_objects_list(objects_arr)
    selected_object = None
    if oid is not None:
        selected_object = get_object_by_id(session_ms, oid, "lsst")

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={"request": request, "objects": objects_list, "selected_object": selected_object},
    )
