import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
from core.services.object import get_mag_stats

router = APIRouter()
templates = Jinja2Templates(
    directory="src/magstats_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8002"
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
        mag_stats_dict[f"band_{i+1}"] = {
            "stellar": mag_stat.stellar,
            "corrected": mag_stat.corrected,
            "ndet": mag_stat.ndet,
            "ndubious": mag_stat.ndubious,
            "magmean": mag_stat.magmean,
            "magmax": mag_stat.magmax,
            "magmin": mag_stat.magmin,
            "magsigma": mag_stat.magsigma,
            "maglast": mag_stat.maglast,
            "magfirst": mag_stat.magfirst,
            "firstmjd": mag_stat.firstmjd,
            "lastmjd": mag_stat.lastmjd,
            "step_id_corr": mag_stat.step_id_corr,
            "fid": mag_stat.fid,
        }

    return templates.TemplateResponse(
        name="magstatRebuild.html.jinja",
        context={"request": request, "stat_r": mag_stats_dict},
    )
