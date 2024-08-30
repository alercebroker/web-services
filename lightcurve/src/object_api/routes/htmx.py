import os
from core.exceptions import ObjectNotFound

from core.services.object import get_object
from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)


@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(request: Request, oid: str):
    try:
        object_data = get_object(
            oid, session_factory=request.app.state.psql_session
        )
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="basicInformationPreview.html.jinja",
        context={
            "request": request,
            "object": object_data.oid,
            "corrected": "Yes" if object_data.corrected else "No",
            "stellar": "Yes" if object_data.stellar else "No",
            "detections": object_data.ndet,
            "nonDetections": "0",
            "discoveryDateMJD": object_data.firstmjd,
            "lastDetectionMJD": object_data.lastmjd,
            "ra": object_data.meanra,
            "dec": object_data.meandec,
        },
    )
