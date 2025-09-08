import traceback
from typing import List

from fastapi import APIRouter, HTTPException

from core.config.dependencies import db_dependency
from core.idmapper.idmapper import catalog_oid_to_masterid

from ..services.conesearch import conesearch as service
from ..models.object import ApiObject

router = APIRouter()


@router.get("/conesearch_oid/objects")
def conesearch(
    oid: str,
    survey: str,
    radius: float,
    neighbors: int,
    db: db_dependency,
) -> List[ApiObject]:
    try:
        id = catalog_oid_to_masterid(survey, oid, True)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid object ID")

    try:
        return service.conesearch_oid(id, radius, neighbors, db.session)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
