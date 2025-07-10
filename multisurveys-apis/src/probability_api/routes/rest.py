import traceback
from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request
from ..services.probability import get_probability

router = APIRouter()

@router.get("/")
async def ping():
    return "This is the probability API"

@router.get("/probability")
async def ping(
    request: Request,
    oid: str,
    classifier: str|None = None,
):
    probability = get_probability(oid, classifier, session_factory=request.app.state.psql_session)
    
    if not probability:
        raise HTTPException(status_code=404, detail="Probability not found for the given OID") 
    
    return probability