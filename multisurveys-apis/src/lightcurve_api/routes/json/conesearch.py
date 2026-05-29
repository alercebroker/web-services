import traceback
from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query

from core.config.dependencies import db_dependency
from core.idmapper import idmapper

from ...models.lightcurve import Lightcurve
from ...models.object import ApiObject
from ...services.conesearch import conesearch as service

router = APIRouter(prefix="/conesearch")

SurveyQuery = Annotated[
    str,
    Query(description="Survey the object belongs to. Allowed values: `ztf`, `lsst` (case-insensitive)."),
]
RadiusQuery = Annotated[float, Query(description="Cone search radius, in degrees.", examples=[0.0083])]
NeighborsQuery = Annotated[int, Query(description="Maximum number of neighboring sources to return.", examples=[2])]


@router.get(
    "/objects_by_oid",
    summary="Find neighboring objects by object id",
    description=(
        "Cone search around a given object: returns catalog objects within `radius` "
        "degrees of that object's mean position, up to `neighbors` matches."
    ),
)
def conesearch(
    oid: Annotated[str, Query(description="ALeRCE object identifier to center the search on.")],
    survey: SurveyQuery,
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
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


@router.get(
    "/objects_by_coordinates",
    summary="Find objects by sky coordinates",
    description=(
        "Cone search around a sky position: returns catalog objects within `radius` "
        "degrees of (`ra`, `dec`), up to `neighbors` matches."
    ),
)
def conesearch_coordinates(
    ra: Annotated[float, Query(description="Right ascension of the search center (ICRS), in degrees.")],
    dec: Annotated[float, Query(description="Declination of the search center (ICRS), in degrees.")],
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
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


@router.get(
    "/lightcurve_by_oid",
    summary="Lightcurve via cone search around an object",
    description=(
        "Returns the combined lightcurve (detections, non-detections and forced "
        "photometry) for sources within `radius` degrees of the given object, up to "
        "`neighbors` neighbors."
    ),
)
def conesearch_oid_lightcurve(
    oid: Annotated[str, Query(description="ALeRCE object identifier to center the search on.")],
    survey: SurveyQuery,
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
    db: db_dependency,
) -> Lightcurve:
    try:
        return service.conesearch_oid_lightcurve(oid, radius, neighbors, survey, db.session)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
