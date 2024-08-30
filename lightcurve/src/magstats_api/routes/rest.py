import os
from core.exceptions import ObjectNotFound

from core.services.object import get_mag_stats
from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["OAPI_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8000"
)


@router.get("/mag/{oid}", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str):
    try:
        mag_stats = get_mag_stats(
            oid, session_factory=request.app.state.psql_session
        )
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")

    mag_stats_dict = {}
    for i, mag_stat in enumerate(mag_stats):
        mag_stats_dict[
            f"band_{i+1}"
        ] = (
            mag_stat.__dict__
        )  ## Es necesario cambiar el nombre de las keys por los fid y trabajar con el conversor que esta en probability en alerts-api

    return {"request": request, "stat_r": mag_stats_dict}
