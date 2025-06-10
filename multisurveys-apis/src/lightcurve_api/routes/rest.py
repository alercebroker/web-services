import traceback
from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request
from ..services.lightcurve_service import get_detections, get_non_detections
from ..services.validations import *

router = APIRouter()


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/detections")
def detections(
    request: Request,
    oid: str,
    survey_id: str,
):
    try:
        survey_validate(survey_id)

        session_init = request.app.state.psql_session

        detections = get_detections(
            oid=oid,
            survey_id=survey_id,
            session_factory=session_init,
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
    request: Request,
    oid: str,
    survey_id: str,
):
    try:
        survey_validate(survey_id)

        session = request.app.state.psql_session

        response = get_non_detections(
            oid=oid,
            survey_id=survey_id,
            session_factory=session,
        ) 

        return response
    
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


    
