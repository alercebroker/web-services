import os
import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..services.aladin_services import get_object_by_id
from ..services.aladin_parser import loads_objects_list
from core.idmapper.idmapper import encode_ids


router = APIRouter(prefix="/htmx")
templates = Jinja2Templates(directory="src/aladin_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8006")


@router.post("/aladin", response_class=HTMLResponse)
async def object_probability_app(request: Request, oid: str, survey: str, objects_arr: Optional[str] = Form(None)):
    try:
        session_ms = request.app.state.psql_session

        master_oid = encode_ids(survey, [oid])

        objects_list = loads_objects_list(objects_arr)

        selected_object = get_object_by_id(session_ms, int(master_oid[0]), "")
    except HTTPException:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")

    return templates.TemplateResponse(
        name="layout.html.jinja",
        context={"request": request, "objects": objects_list, "selected_object": selected_object},
    )
