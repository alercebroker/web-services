from dependency_injector import containers, providers
from astroobject.core.shared.sql import Database
from astroobject.core.ioc.container import AstroObjectContainer

class ApiContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[]
    )

    config = providers.Configuration()
    psql_db = providers.ThreadSafeSingleton(
        Database, config.DATABASE.SQL
    )

    astroobject_service = providers.Container(
        AstroObjectContainer, db_session=psql_db
    )
    
