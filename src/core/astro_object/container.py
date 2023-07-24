from dependency_injector import containers, providers
from core.astro_object.infrastructure.object_list_repository import (
    ObjectListRepository,
)
from core.astro_object.domain.astro_object_service import AstroObjectService
from core.astro_object.use_case.get_object_list import GetObjectList


class AstroObjectContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency()
    object_list_repository = providers.Factory(
        ObjectListRepository, session_factory=session_factory
    )
    astro_object_service = providers.Factory(
        AstroObjectService,
        object_list_repository=object_list_repository,
        object_repository=None,
    )
    get_object_list_command = providers.Factory(
        GetObjectList, service=astro_object_service
    )
