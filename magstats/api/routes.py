from fastapi import Request, APIRouter
from core.service import get_magstats
from .result_handler import handle_success, handle_error
from database.sql import session
from database.mongo import database

router = APIRouter()


@router.get("/")
def root():
    return "this is the magstats module"


@router.get("/magstats/{oid}")
def magstats(
    request: Request,
    oid: str,
    survey_id: str = "ztf",
):
    return get_magstats(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
    )


