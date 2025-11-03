from fastapi import APIRouter, Request
from fastapi import HTTPException
from ..services.magstats import get_magstats
from .temporal_utils import mag_parser, parse_lsst_dia_objects_to_dict

router = APIRouter()


@router.get("/")
async def ping():
    return "This is the magstats API"


@router.get("/magstats")
async def magstats(request: Request, oid: str, survey_id: str):
    mag_stats_raw = get_magstats(oid, survey_id, session_factory=request.app.state.psql_session)

    if survey_id == "ztf":
        magstats = mag_parser(mag_stats_raw)
        for d in magstats:
            del d["fid"]
    elif survey_id == "lsst":
        magstats = parse_lsst_dia_objects_to_dict(mag_stats_raw)
        del magstats[0]["created_date"]

    if not magstats:
        raise HTTPException(status_code=404, detail="Magstats not found for the given OID")
    print("magstats", magstats)
    return magstats
