import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from core.static_files import configure_templates
from fastapi.responses import HTMLResponse
from ..services.aladin_services import prepare_aladin_data
from ..models.object import RawObjectsRequest


router = APIRouter(prefix="/htmx")
templates = Jinja2Templates(directory="src/aladin_api/templates", autoescape=True, auto_reload=True)
configure_templates(templates, "http://localhost:8006")


@router.post("/aladin", response_class=HTMLResponse)
def object_probability_app(request: Request, oid: str, survey: str, objects_arr: Optional[str] = Form(None)):
    try:
        session_ms = request.app.state.psql_session

        raw_objects_request = RawObjectsRequest(selected_oid=oid, sid=survey, objects=objects_arr)

        objects_list, selected_object = prepare_aladin_data(session_ms, raw_objects_request)
    except HTTPException:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={"request": request, "objects": objects_list, "selected_object": selected_object},
    )
