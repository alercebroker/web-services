import traceback
from fastapi import APIRouter, HTTPException

from ..services.lightcurve_service import (
    get_detections,
    get_forced_photometry,
    get_lightcurve,
    get_non_detections,
)
from ..services.validations import survey_validate
from core.config.dependencies import db_dependency

router = APIRouter()


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/detections")
def detections(
    oid: str,
    survey_id: str,
    db: db_dependency,
):
    try:
        survey_validate(survey_id)

        detections = get_detections(
            oid=oid,
            survey_id=survey_id,
            session_factory=db.session,
        )

        return detections

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
    oid: str,
    survey_id: str,
    db: db_dependency,
):
    try:
        survey_validate(survey_id)

        response = get_non_detections(
            oid=oid,
            survey_id=survey_id,
            session_factory=db.session,
        )

        return response

    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/forced-photometry")
def forced_photometry(
    oid: str,
    survey_id: str,
    db: db_dependency,
):
    try:
        survey_validate(survey_id)

        forced_photometry_data = get_forced_photometry(
            oid=oid,
            survey_id=survey_id,
            session_factory=db.session,
        )

        return forced_photometry_data

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
    oid: str,
    survey_id: str,
    db: db_dependency,
):
    try:
        survey_validate(survey_id)
        response = get_lightcurve(
            oid=oid,
            survey_id=survey_id,
            session_factory=db.session,
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
