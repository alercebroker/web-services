import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
# from core.repository.queries.magstats import get_magstats_by_oid
from ..services.magstats import get_magstats
from .temporal_utils import mag_parser, parse_lsst_dia_objects_to_dict
import warnings


router = APIRouter()
templates = Jinja2Templates(directory=os.path.abspath("src/magstat_api/templates"), autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8002")


@router.get("/htmx/mag", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str, survey_id=None):
    bandMapping = {
        1: "g",
        2: "r",
        3: "i",
    };

    if survey_id == None:
        survey_id = "ztf"
        warnings.warn(
            "survey not provided, defaulting to 'ztf'. This will use the legacy ZTF client. This behavior will be deprecated in future versions.",
            DeprecationWarning,
        )

    try:
        mag_stats_raw = get_magstats(
            oid, survey_id, session_factory=request.app.state.psql_session
        ) 
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object not found")
    if survey_id == "ztf":
        mag_stats = mag_parser(mag_stats_raw)
        for d in mag_stats:
            del d['fid']
    elif survey_id == "lsst":
        mag_stats = parse_lsst_dia_objects_to_dict(mag_stats_raw)
        del mag_stats[0]["created_date"]

    mag_keys = list(mag_stats[0].keys())

    return templates.TemplateResponse(
        name="magstatRebuild.html.jinja",
        context={"request": request, "stat_r": mag_stats, 'stat_r_keys': mag_keys, 'band_mapping': bandMapping},
    )
