from dependency_injector import containers, providers
from db_plugins.db.mongo.connection import MongoConnection
from core.light_curve.container import LightCurveContainer
from core.astro_object.container import AstroObjectContainer
from core.probabilities.container import ProbabilitiesContainer
from core.features.container import FeaturesContainer
from core.magstats.container import MagStatsContainer
from core.classifier.container import ClassifierContainer
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
    config = providers.Configuration()

    # gateways
    mongo_db = providers.ThreadSafeSingleton(MongoConnection)
    database_config = config.DATABASE
    db_control = providers.ThreadSafeSingleton(
        DBControl,
        mongo_config=database_config.MONGO,
        mongo_db=mongo_db,
    )

    # views dependencies
    view_result_handler = providers.Factory(ViewResultHandler)

    # packages
    lightcurve_package = providers.Container(LightCurveContainer, db=mongo_db)
    astro_object_package = providers.Container(
        AstroObjectContainer, db=mongo_db
    )
    probabilities_package = providers.Container(
        ProbabilitiesContainer, db=mongo_db
    )
    features_package = providers.Container(FeaturesContainer, db=mongo_db)
    magstats_package = providers.Container(MagStatsContainer, db=mongo_db)
    classifier_package = providers.Container(ClassifierContainer, db=mongo_db)
