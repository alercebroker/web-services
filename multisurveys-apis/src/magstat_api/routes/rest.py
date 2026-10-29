from fastapi import APIRouter, HTTPException, Request

from core.idmapper.idmapper import parse_oid
from core.idmapper.survey_mapper import Survey

from ..services.magstats import get_magstats
from .temporal_utils import mag_parser, parse_lsst_dia_objects_to_dict

router = APIRouter()


@router.get("/")
def ping():
    return "This is the magstats API"


@router.get("/magstats")
def magstats(request: Request, oid: str, survey_id: Survey):
    master_id = parse_oid(survey_id, oid)
    mag_stats_raw = get_magstats(master_id, survey_id, session_factory=request.app.state.psql_session)

    if survey_id == "ztf":
        magstats = mag_parser(mag_stats_raw)
        for d in magstats:
            d["band"] = d.pop("fid")  # each row says its band (1=g, 2=r, 3=i)
    elif survey_id == "lsst":
        magstats = parse_lsst_dia_objects_to_dict(mag_stats_raw)
        if magstats:
            del magstats[0]["created_date"]

    if not magstats:
        raise HTTPException(status_code=404, detail="Magstats not found for the given OID")

    return magstats
