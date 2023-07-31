from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi import Depends

from core.application.astroobject_service import AstroObjectService
from core.domain.astroobject_queries import GetAstroObjectsQuery
from .container import ApiContainer
from .dto.output import astrooobjects_response_factory

router = APIRouter()

@router.get("/objects")
@inject
async def get_astro_objects(
    query: GetAstroObjectsQuery = Depends(),
    service: AstroObjectService = Depends(
        Provide[ApiContainer.astroobject.astroobject_service]
    ),
):
    result = service.get_objects(query)
    result = result.to_dict()
    result["items"] = [astrooobjects_response_factory(item) for item in result["items"]]
    return result


@router.get("/object")
def get_astro_object():
    return {}