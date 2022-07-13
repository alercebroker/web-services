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

    repo_single_object = providers.Factory(SingleAstroObjectRepository, db=db)
    repo_object_list = providers.Factory(ListAstroObjectRepository, db=db)

    service = providers.Factory(
        AstroObjectService,
        repo_single_object=repo_single_object,
        repo_object_list=repo_object_list
    )

    get_single_object = providers.Factory(
        GetSingleAstroObject, service=service
    )
    get_object_list = providers.Factory(GetListAstroObject, service=service)
