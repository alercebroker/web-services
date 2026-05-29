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
from ...services.validations import Survey, survey_validate

router = APIRouter()

SurveyQuery = Annotated[Survey, Query(description="Survey the object belongs to.")]
OidQuery = Annotated[
    list[str],
    Query(
        description="ALeRCE object identifier(s). Repeat the parameter to request "
        "several objects in a single call (e.g. `?oid=A&oid=B`).",
        examples=["170433140619739440"],
    ),
]


@router.get("/")
def root():
    return "this is the lightcurve module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get(
    "/detections",
    summary="Detections (difference-image alerts)",
    description=(
        "Significant (typically >5σ) flux measurements on the **difference image** "
        "(science image minus a reference template) for the given object(s). Each "
        "detection is one alert epoch in a single band. Survey-specific columns are "
        "included (e.g. ZTF `magpsf`/`sigmapsf`, LSST `psfFlux`/`snr`)."
    ),
)
def detections(
    survey_id: SurveyQuery,
    db: db_dependency,
    oid: OidQuery,
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


@router.get(
    "/non_detections",
    summary="Non-detections (upper limits)",
    description=(
        "Epochs where the object was observed but **not** significantly detected, "
        "reported as the 5σ limiting magnitude (`diffmaglim`) of the difference image. "
        "These constrain the object's brightness when it was not detected. Currently "
        "available for ZTF."
    ),
)
def non_detections(
    survey_id: SurveyQuery,
    db: db_dependency,
    oid: OidQuery,
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


@router.get(
    "/forced-photometry",
    summary="Forced photometry",
    description=(
        "Flux measured at the object's **fixed position** on every available image, "
        "whether or not that epoch triggered a detection. Produces a uniformly sampled "
        "lightcurve that includes faint and negative-flux epochs. ZTF reports corrected "
        "magnitudes; LSST reports `psfFlux`/`scienceFlux`."
    ),
)
def forced_photometry(
    survey_id: SurveyQuery,
    db: db_dependency,
    oid: OidQuery,
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


@router.get(
    "/lightcurve",
    summary="Full lightcurve (detections + non-detections + forced photometry)",
    description=(
        "Convenience endpoint returning all three photometric products for the "
        "object(s) in a single response, under the keys `detections`, "
        "`non_detections` and `forced_photometry`."
    ),
)
def lightcurve(
    survey_id: SurveyQuery,
    db: db_dependency,
    oid: OidQuery,
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
            response["non_detections"] = get_non_detections(oid[0], survey_id, db.session)
            response["forced_photometry"] = get_forced_photometry(oid[0], survey_id, db.session)
        else:
            response["detections"] = get_detections_by_list(oid, survey_id, db.session)
            response["non_detections"] = get_non_detections_by_list(oid, survey_id, db.session)
            response["forced_photometry"] = get_forced_photometry_by_list(oid, survey_id, db.session)

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
