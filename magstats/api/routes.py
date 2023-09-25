from fastapi import Request, APIRouter
from core.service import get_magstats
from .result_handler import handle_success, handle_error
from database.sql import session

router = APIRouter()


@router.get("/")
def root():
    return "this is the magstats module"


@router.get("/magstats/{oid}")
def magstats(
    request: Request,
    oid: str,
):
    return get_magstats(
        oid=oid,
        session_factory=session,
        handle_success=handle_success,
        handle_error=handle_error,
    )
