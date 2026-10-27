from fastapi import APIRouter, HTTPException, Request
from core.static_files import configure_templates, html_templates
from fastapi.responses import HTMLResponse
from ..services.crossmatch_service import get_cross_for_frontend
from ..models.object import ObjectInformation


router = APIRouter()
templates = html_templates("src/crossmatch_api/templates")
configure_templates(templates, "http://localhost:8005")


@router.get("/htmx/crossmatch", response_class=HTMLResponse)
def object_mag_app(request: Request, oid: str, survey_id: str):
    session = request.app.state.psql_session

    object_details = ObjectInformation(oid=oid, survey=survey_id)

    unavailable = False
    try:
        cross, cross_keys = get_cross_for_frontend(object_details, session)
    except HTTPException as error:
        if error.status_code not in (502, 504):
            raise
        # catsHTM is down or slow: show the card with "-" instead of failing the whole card
        cross, cross_keys, unavailable = [], [], True

    return templates.TemplateResponse(
        request=request,
        name="crossmatch.html.jinja",
        context={
            "request": request,
            "cross": cross,
            "crossKeys": cross_keys,
            "unavailable": unavailable,
        },
    )
