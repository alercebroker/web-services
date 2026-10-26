from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from core.static_files import configure_templates, html_templates

from ..models.object import RawObjectsRequest
from ..services.aladin_services import prepare_aladin_data

router = APIRouter(prefix="/htmx")
templates = html_templates("src/aladin_api/templates")
configure_templates(templates, "http://localhost:8006")


@router.post("/aladin", response_class=HTMLResponse)
def object_probability_app(request: Request, oid: str, survey: str, objects_arr: str | None = Form(None)):
    session_ms = request.app.state.psql_session

    raw_objects_request = RawObjectsRequest(selected_oid=oid, sid=survey, objects=objects_arr)

    objects_list, selected_object = prepare_aladin_data(session_ms, raw_objects_request)

    return templates.TemplateResponse(
        request=request,
        name="layout.html.jinja",
        context={"request": request, "objects": objects_list, "selected_object": selected_object},
    )
