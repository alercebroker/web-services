import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
# from core.repository.queries.magstats import get_magstats_by_oid
from ..services.magstats import get_magstats
from core.repository.dummy_data import magstats_dummy
from .temporal_utils import mag_parser


router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath("src/magstat_api/templates"), autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8002"
)


@router.get("/htmx/mag", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str):



    try:
        mag_stats_raw = get_magstats(
            oid, session_factory=request.app.state.psql_session
        )
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")
    mag_stats = mag_parser(mag_stats_raw)

    mag_stats_dict = {}

    for mag_stat in mag_stats:
        mag_stats_dict[f"band_{mag_stat['fid']}"] = {
            "stellar": mag_stat['stellar'],
            "corrected": mag_stat['corrected'],
            "ndet": mag_stat['ndet'],
            "ndubious": mag_stat['ndubious'],
            "magmean": mag_stat['magmean'],
            "magmedian": mag_stat['magmedian'],
            "magmax": mag_stat['magmax'],
            "magmin": mag_stat['magmin'],
            "magsigma": mag_stat['magsigma'],
            "maglast": mag_stat['maglast'],
            "magfirst": mag_stat['magfirst'],
            "firstmjd": mag_stat['firstmjd'],
            "lastmjd": mag_stat['lastmjd'],
            "step_id_corr": mag_stat['step_id_corr'],
            "fid": mag_stat['fid'],
        }

    # mag_stats_dict = magstats_dummy

    return templates.TemplateResponse(
        name="magstatRebuild.html.jinja",
        context={"request": request, "stat_r": mag_stats_dict},
    )
