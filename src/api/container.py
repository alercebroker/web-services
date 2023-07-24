from dependency_injector import containers, providers
from core.light_curve.container import LightcurveContainer
from core.astro_object.container import AstroObjectContainer
from api.result_handlers.view_result_handler import ViewResultHandler
from shared.database.sql import Database as SQLDatabase
from shared.database.mongo import Database as MongoDatabase


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.resources.astro_object.astro_object",
            "api.resources.classifier.classifier",
            "api.resources.features.features",
            "api.resources.magstats.magstats",
            "api.resources.light_curve.light_curve",
            "api.resources.probabilities.probabilities",
        ]
    )
    # config
    config = providers.Configuration()

    # gateways
    database_config = config.DATABASE
    psql_db = providers.ThreadSafeSingleton(SQLDatabase, database_config.SQL)
    mongo_db = providers.ThreadSafeSingleton(
        MongoDatabase, database_config.MONGO)

    # views dependencies
    view_result_handler = providers.Factory(ViewResultHandler)

    # packages
    lightcurve_package = providers.Container(
        LightcurveContainer, session_factory=psql_db.provided.session, mongo_db=mongo_db.provided.mongo_db
    )
    astro_object_package = providers.Container(
        AstroObjectContainer, session_factory=psql_db.provided.session
    )
