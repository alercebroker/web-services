from dependency_injector import containers, providers
from db_plugins.db.sql.connection import SQLConnection
from db_plugins.db.mongo.connection import MongoConnection
from core.light_curve.container import LightcurveContainer
from shared.database.control import DBControl
from api.result_handlers.view_result_handler import ViewResultHandler


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
    config = providers.Configuration(yaml_files=["config.yml"])

    # gateways
    psql_db = providers.ThreadSafeSingleton(SQLConnection)
    mongo_db = providers.ThreadSafeSingleton(MongoConnection)
    database_config = config.DATABASE
    db_control = providers.Singleton(
        DBControl,
        app_config=database_config.APP_CONFIG,
        psql_config=database_config.SQL,
        mongo_config=database_config.MONGO,
        psql_db=psql_db,
        mongo_db=mongo_db,
    )

    # views dependencies
    view_result_handler = providers.Factory(ViewResultHandler)

    # packages
    lightcurve_package = providers.Container(
        LightcurveContainer, psql_db=psql_db, mongo_db=mongo_db
    )
