import traceback
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from core.config.dependencies import db_dependency

from ...services.lightcurve_service import (
    get_detections,
    get_detections_by_list,
    get_forced_photometry,
    get_forced_photometry_by_list,
    get_non_detections,
    get_non_detections_by_list,
)
from ...services.validations import survey_validate

router = APIRouter()


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/detections")
def detections(
    survey_id: str,
    db: db_dependency,
    oid: Annotated[list[str], Query()],
):
    try:
        survey_validate(survey_id)

        if len(oid) == 1:
            return get_detections(
                oid=oid[0],
                survey_id=survey_id,
                session_factory=db.session,
            )
        else:
            return get_detections_by_list(oid, survey_id, db.session)

    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/non_detections")
def non_detections(
    survey_id: str,
    db: db_dependency,
    oid: Annotated[list[str], Query()],
):
    try:
        survey_validate(survey_id)

        if len(oid) == 1:
            return get_non_detections(
                oid=oid[0],
                survey_id=survey_id,
                session_factory=db.session,
            )
        else:
            return get_non_detections_by_list(oid, survey_id, db.session)

    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/forced-photometry")
def forced_photometry(
    survey_id: str,
    db: db_dependency,
    oid: Annotated[list[str], Query()],
):
    try:
        survey_validate(survey_id)

        if len(oid) == 1:
            return get_forced_photometry(
                oid=oid[0],
                survey_id=survey_id,
                session_factory=db.session,
            )
        else:
            return get_forced_photometry_by_list(oid, survey_id, db.session)

    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/lightcurve")
def lightcurve(
    survey_id: str,
    db: db_dependency,
    oid: Annotated[list[str], Query()],
):
    try:
        survey_validate(survey_id)
        response = {
            "detections": [],
            "non_detections": [],
            "forced_photometry": [],
        }
        if len(oid) == 1:
            response["detections"] = get_detections(oid[0], survey_id, db.session)
            response["non_detections"] = get_non_detections(
                oid[0], survey_id, db.session
            )
            response["forced_photometry"] = get_forced_photometry(
                oid[0], survey_id, db.session
            )
        else:
            response["detections"] = get_detections_by_list(oid, survey_id, db.session)
            response["non_detections"] = get_non_detections_by_list(
                oid, survey_id, db.session
            )
            response["forced_photometry"] = get_forced_photometry_by_list(
                oid, survey_id, db.session
            )

        return response

    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
