from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException
from fastapi import Depends

from core.application.astroobject_service import AstroObjectService
from core.domain.astroobject_queries import GetAstroObjectQuery, GetAstroObjectsQuery
from .container import ApiContainer
from .dto.output import astrooobjects_response_factory

router = APIRouter()


@router.get("/objects/")
@inject
async def get_astro_objects(
    query: GetAstroObjectsQuery = Depends(),
    service: AstroObjectService = Depends(
        Provide[ApiContainer.astroobject.astroobject_service]
    ),
):
    result = await service.get_objects(query)
    result = result.to_dict()
    result["items"] = [astrooobjects_response_factory(item) for item in result["items"]]
    return result


@router.get("/object/{oid}")
@inject
async def get_astro_object(
    query: GetAstroObjectQuery = Depends(),
    service: AstroObjectService = Depends(
        Provide[ApiContainer.astroobject.astroobject_service]
    ),
):
    result = await service.get_object(query)
    if not result:
        raise HTTPException(404)
    return result
