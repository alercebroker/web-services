import os
import warnings

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
from core.idmapper.idmapper import parse_oid
from core.idmapper.survey_mapper import get_survey_id
from core.static_files import configure_templates

from ..services.magstats import get_magstats
from .temporal_utils import mag_parser, parse_lsst_dia_objects_to_dict

router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath("src/magstat_api/templates"),
    autoescape=True,
    auto_reload=True,
)
configure_templates(templates, "http://localhost:8002")


@router.get("/htmx/mag", response_class=HTMLResponse)
def object_mag_app(request: Request, oid: str, survey_id=None):
    bandMapping = {
        1: "g",
        2: "r",
        3: "i",
    }

    if survey_id is None:
        survey_id = "ztf"
        warnings.warn(
            "survey not provided, defaulting to 'ztf'. This will use the legacy ZTF client. This behavior will be deprecated in future versions.",
            DeprecationWarning,
        )

    survey_id = survey_id.lower()
    get_survey_id(survey_id)
    master_id = parse_oid(survey_id, oid)
    mag_stats_raw = get_magstats(master_id, survey_id, session_factory=request.app.state.psql_session)

    bands = None
    if survey_id == "ztf":
        mag_stats = mag_parser(mag_stats_raw)
        # Each row's band labels its column; out of the rows, so it isn't listed as a stat
        bands = [d.pop("fid") for d in mag_stats]
    elif survey_id == "lsst":
        mag_stats = parse_lsst_dia_objects_to_dict(mag_stats_raw)
        if mag_stats:
            del mag_stats[0]["created_date"]

    if not mag_stats:
        raise ObjectNotFound(oid)  # answered as 404 by the central handler

    mag_keys = list(mag_stats[0].keys())

    return templates.TemplateResponse(
        name="magstatRebuild.html.jinja",
        context={
            "request": request,
            "stat_r": mag_stats,
            "stat_r_keys": mag_keys,
            "band_mapping": bandMapping,
            "bands": bands,
        },
    )
