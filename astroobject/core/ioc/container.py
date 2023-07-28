from dependency_injector import containers, providers
from core.application.astroobject_service import AstroObjectService
from core.infrastructure.astroobject_sql_repository import AstroObjectSQLRespository


class AstroObjectContainer(containers.DeclarativeContainer):
    db_session = providers.Dependency()
    astroobject_repository = providers.Factory(
        AstroObjectSQLRespository, db_session=db_session
    )

    # service
    astroobject_service = providers.Factory(
        AstroObjectService, astroobject_repository=astroobject_repository
    )
