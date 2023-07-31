from dependency_injector import containers, providers
from core.shared.sql import Database
from core.ioc.container import AstroObjectContainer


class ApiContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.routes",
        ]
    )

    config = providers.Configuration("config.yml")
    psql_db = providers.ThreadSafeSingleton(Database, config.DATABASE.SQL)

    astroobject = providers.Container(AstroObjectContainer, db_client=psql_db)
