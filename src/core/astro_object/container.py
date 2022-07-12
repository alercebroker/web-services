from dependency_injector import containers, providers
from db_plugins.db.mongo.connection import MongoConnection

from .domain import AstroObjectService
from .infrastructure import (
    ListAstroObjectRepository,
    SingleAstroObjectRepository
)
from .use_case import GetSingleAstroObject, GetListAstroObject


class AstroObjectContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repository_single = providers.Factory(SingleAstroObjectRepository, db=db)
    repository_list = providers.Factory(ListAstroObjectRepository, db=db)

    service = providers.Factory(
        AstroObjectService,
        single_repository=repository_single,
        list_repository=repository_list
    )

    command_single = providers.Factory(GetSingleAstroObject, service=service)
    command_list = providers.Factory(GetListAstroObject, service=service)
