from typing import Annotated

from fastapi import APIRouter, Query

from core.config.dependencies import db_dependency
from core.idmapper.survey_mapper import SurveyQuery
from core.idmapper import idmapper

from ...models.object import ApiObject
from ...services.conesearch import conesearch as service
from .missing_values import json_rows

router = APIRouter(prefix="/conesearch")

RadiusQuery = Annotated[float, Query(gt=0, description="Cone search radius, in degrees.", examples=[0.0083])]
NeighborsQuery = Annotated[
    int, Query(gt=0, description="Maximum number of neighboring sources to return.", examples=[2])
]


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
    survey_id: SurveyQuery,
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
    db: db_dependency,
) -> list[ApiObject]:
    id = idmapper.parse_oid(survey_id, oid)
    return service.conesearch_oid(id, radius, neighbors, db.session)


@router.get(
    "/objects_by_coordinates",
    summary="Find objects by sky coordinates",
    description=(
        "Cone search around a sky position: returns catalog objects within `radius` "
        "degrees of (`ra`, `dec`), up to `neighbors` matches."
    ),
)
def conesearch_coordinates(
    ra: Annotated[float, Query(ge=0, le=360, description="Right ascension of the search center (ICRS), in degrees.")],
    dec: Annotated[float, Query(ge=-90, le=90, description="Declination of the search center (ICRS), in degrees.")],
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
    db: db_dependency,
):
    return service.conesearch_coordinates(ra, dec, radius, neighbors, db.session)


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
    survey_id: SurveyQuery,
    radius: RadiusQuery,
    neighbors: NeighborsQuery,
    db: db_dependency,
):
    lightcurve = service.conesearch_oid_lightcurve(oid, radius, neighbors, survey_id, db.session)
    return {key: json_rows(getattr(lightcurve, key)) for key in ("detections", "non_detections", "forced_photometry")}
