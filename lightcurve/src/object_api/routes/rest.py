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
templates.env.globals["OAPI_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8001"
)


@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(request: Request, oid: str):
    link = "https://acortar.link/ba5kba"

    try:
        object_data = get_object(
            oid, session_factory=request.app.state.psql_session
        )
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return {
        "request": request,
        "object": object_data.oid,
        "corrected": object_data.corrected,
        "stellar": object_data.stellar,
        "detections": object_data.ndet,
        "discoveryDateMJD": object_data.firstmjd,
        "lastDetectionMJD": object_data.lastmjd,
        "ra": object_data.meanra,
        "dec": object_data.meandec,
        "link": link,
    }
