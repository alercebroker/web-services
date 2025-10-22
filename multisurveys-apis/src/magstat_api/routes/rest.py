from fastapi import APIRouter, Request
from fastapi import HTTPException
from ..services.magstats import get_magstats

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
    magstats = get_magstats(oid, survey_id, session_factory=request.app.state.psql_session)

    if not magstats:
        raise HTTPException(status_code=404, detail="Magstats not found for the given OID")

    return magstats
