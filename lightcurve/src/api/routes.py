from fastapi import Request, APIRouter
from ralidator_fastapi.decorators import (
    set_filters_decorator,
    check_permissions_decorator,
    set_permissions_decorator,
)
from core.service import get_detections, get_non_detections, get_lightcurve
from .result_handler import handle_success, handle_error
from database.sql import session
from database.mongo import database

router = APIRouter()


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/detections/{oid}")
@set_permissions_decorator(["admin", "basic_user"])
@set_filters_decorator(["filter_atlas_detections"])
@check_permissions_decorator
def detections(
    request: Request,
    oid: str,
    survey_id: str = "ztf",
):
    return get_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )


@router.get("/non_detections/{oid}")
@set_permissions_decorator(["admin", "basic_user"])
@set_filters_decorator(["filter_atlas_non_detections"])
@check_permissions_decorator
def non_detections(
    oid: str,
    request: Request,
    survey_id: str = "ztf",
):
    return get_non_detections(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )


@router.get("/lightcurve/{oid}")
@set_permissions_decorator(["admin", "basic_user"])
@set_filters_decorator(["filter_atlas_lightcurve"])
@check_permissions_decorator
def lightcurve(
    oid: str,
    request: Request,
    survey_id: str = "ztf",
):
    return get_lightcurve(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
