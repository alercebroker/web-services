import traceback
from typing import List

from fastapi import APIRouter, HTTPException

from core.config.dependencies import db_dependency
from core.idmapper import idmapper

from ...models.lightcurve import Lightcurve
from ...models.object import ApiObject
from ...services.conesearch import conesearch as service

router = APIRouter(prefix="/conesearch")


@router.get("/objects_by_oid")
def conesearch(
    oid: str,
    survey: str,
    radius: float,
    neighbors: int,
    db: db_dependency,
) -> List[ApiObject]:
    try:
        id = idmapper.catalog_oid_to_masterid(survey, oid, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = service.conesearch_oid(id, radius, neighbors, db.session)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/objects_by_coordinates")
def conesearch_coordinates(
    ra: float,
    dec: float,
    radius: float,
    neighbors: int,
    db: db_dependency,
):
    try:
        result = service.conesearch_coordinates(ra, dec, radius, neighbors, db.session)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/lightcurve_by_oid")
def conesearch_oid_lightcurve(
    oid: str, survey: str, radius: float, neighbors: int, db: db_dependency
) -> Lightcurve:
    try:
        return service.conesearch_oid_lightcurve(
            oid, radius, neighbors, survey, db.session
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
