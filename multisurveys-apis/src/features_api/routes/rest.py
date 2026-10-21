from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from core.idmapper.idmapper import parse_oid
from core.idmapper.survey_mapper import get_survey_id
from core.repository.queries.features import get_features, object_exists

from ..models.features import Feature

router = APIRouter()


@router.get("/")
def root():
    return "this is the features module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get(
    "/features",
    summary="Features of an object",
    description=(
        "The light-curve features computed for one object (the light-curve classifier's input), one row per "
        "feature and band. Filter by `name` for a single feature, by `band`, or by `version`."
    ),
    response_model=list[Feature],
)
def features(
    request: Request,
    oid: Annotated[str, Query(description="Object id: a ZTF name (ZTF…) or a numeric id.", examples=["ZTF18aarwvbm"])],
    survey_id: Annotated[str, Query(description="Survey the object belongs to: `ztf` or `lsst`.", examples=["ztf"])],
    name: Annotated[str | None, Query(description="Only this feature (its name).")] = None,
    band: Annotated[int | None, Query(description="Only this band (for ZTF: 1=g, 2=r, 3=i).")] = None,
    version: Annotated[str | None, Query(description="Only this feature version.")] = None,
):
    try:
        sid = get_survey_id(survey_id)
        master_id = parse_oid(survey_id, oid)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    session = request.app.state.psql_session
    if not object_exists(master_id, sid, session):
        raise HTTPException(status_code=404, detail=f"Object {oid} not found")

    return get_features(master_id, sid, session, name=name, band=band, version=version)
