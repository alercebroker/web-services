from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi import Depends

from core.application.astroobject_service import AstroObjectService
from core.domain.astroobject_queries import GetAstroObjectsQuery
from .container import ApiContainer

router = APIRouter()

@router.get("/objects")
@inject
async def get_astro_objects(
    query: GetAstroObjectsQuery = Depends(),
    service: AstroObjectService = Depends(
        Provide[ApiContainer.astroobject_service]
    ),
):
    result = service.get_objects(query)
    print([item.model_dump() for item in result.items])
    # return [item.model_dump() for item in result.items]
    return {}


@router.get("/object")
def get_astro_object():
    return {}