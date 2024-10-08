from fastapi import APIRouter, Request
from ralidator_fastapi.decorators import (
    check_permissions_decorator,
    set_filters_decorator,
    set_permissions_decorator,
)

from core.services.lightcurve_service import (
    get_detections,
    get_forced_photometry,
    get_lightcurve,
    get_non_detections,
)

from ..result_handler import handle_error, handle_success

router = APIRouter()


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/detections/{oid}")
@set_permissions_decorator(["admin", "basic_user"])
@set_filters_decorator(["filter_atlas_detections"])
@check_permissions_decorator
def detections(
    request: Request,
    oid: str,
    survey_id: str = "all",
):
    session = request.app.state.psql_session
    database = request.app.state.mongo_db
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
    survey_id: str = "all",
):
    session = request.app.state.psql_session
    database = request.app.state.mongo_db
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
    survey_id: str = "all",
):
    session = request.app.state.psql_session
    database = request.app.state.mongo_db
    return get_lightcurve(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )


@router.get("/forced-photometry/{oid}")
@set_permissions_decorator(["admin", "basic_user"])
@set_filters_decorator(["filter_atlas_forced_photometry"])
@check_permissions_decorator
def forced_photometry(oid: str, request: Request, survey_id: str = "all"):
    session = request.app.state.psql_session
    database = request.app.state.mongo_db
    return get_forced_photometry(
        oid=oid,
        survey_id=survey_id,
        session_factory=session,
        mongo_db=database,
        handle_error=handle_error,
        handle_success=handle_success,
    )
