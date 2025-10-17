from fastapi import APIRouter, Request
from fastapi import HTTPException
from ..services.magstats import get_magstats
from core.repository.dummy_data import magstats_dummy
from .temporal_utils import mag_parser, parse_lsst_dia_objects_to_dict
from core.exceptions import ObjectNotFound

router = APIRouter()


@router.get("/")
async def ping():
    return "This is the magstats API"


@router.get("/magstats")
async def magstats(
    request: Request,
    oid: str,
    survey_id: str
):
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

    return mag_stats
