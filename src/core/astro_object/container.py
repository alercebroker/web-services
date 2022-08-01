from dependency_injector import containers, providers
from db_plugins.db.mongo.connection import MongoConnection

from .domain import AstroObjectService
from . import infrastructure, use_case


class AstroObjectContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_single_object = providers.Factory(
        infrastructure.SingleAstroObjectRepository, db=db
    )
    repo_object_list = providers.Factory(
        infrastructure.ListAstroObjectRepository, db=db
    )
    repo_limits = providers.Factory(infrastructure.LimitsRepository, db=db)

    service = providers.Factory(
        AstroObjectService,
        repo_single_object=repo_single_object,
        repo_object_list=repo_object_list,
        repo_limits=repo_limits,
    )

    get_single_object = providers.Factory(
        use_case.GetSingleAstroObject, service=service
    )
    get_object_list = providers.Factory(
        use_case.GetListAstroObject, service=service
    )
    get_limits = providers.Factory(
        use_case.GetLimits, service=service
    )
