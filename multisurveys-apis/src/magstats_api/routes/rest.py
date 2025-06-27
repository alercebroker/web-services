import traceback
from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request
from ..services.magstats import get_magstats_by_oid

router = APIRouter()

@router.get("/")
async def ping():
    return "This is the magstats API"

@router.get("/magstats")
async def ping(
    request: Request,
    oid: str,
):
    magstats = get_magstats_by_oid(oid, session_factory=request.app.state.psql_session)
    
    if not magstats:
        raise HTTPException(status_code=404, detail="Magstats not found for the given OID") 
    
    return magstats
