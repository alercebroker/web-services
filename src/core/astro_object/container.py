from dependency_injector import containers, providers
from db_plugins.db.mongo.connection import MongoConnection

from .domain import AstroObjectService
from .infrastructure import (
    ListAstroObjectRepository,
    SingleAstroObjectRepository,
    LimitsRepository
)
from .use_case import GetSingleAstroObject, GetListAstroObject, GetLimits


class AstroObjectContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_single_object = providers.Factory(SingleAstroObjectRepository, db=db)
    repo_object_list = providers.Factory(ListAstroObjectRepository, db=db)
    repo_limits = providers.Factory(LimitsRepository, db=db)

    service = providers.Factory(
        AstroObjectService,
        repo_single_object=repo_single_object,
        repo_object_list=repo_object_list,
        repo_limits=repo_limits
    )

    get_single_object = providers.Factory(
        GetSingleAstroObject, service=service
    )
    get_object_list = providers.Factory(GetListAstroObject, service=service)
    get_limits = providers.Factory(GetLimits, service=service)
