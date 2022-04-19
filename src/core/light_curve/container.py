from dependency_injector import containers, providers
from core.light_curve.infrastructure.detection_repository import (
    PSQLDetectionRepository,
    MongoDetectionRepository,
)
from core.light_curve.infrastructure.non_detection_repository import (
    PSQLNonDetectionRepository,
    MongoNonDetectionRepository,
)
from core.light_curve.domain.lightcurve_service import LightcurveService
from core.light_curve.use_case.get_detection import GetDetection
from core.light_curve.use_case.get_non_detection import GetNonDetection
from core.light_curve.use_case.get_lightcurve import GetLightcurve
from db_plugins.db.sql.connection import SQLConnection
from db_plugins.db.mongo.connection import MongoConnection


class LightcurveContainer(containers.DeclarativeContainer):
    # wiring_config = containers.WiringConfiguration(
    #     modules=["api.resources.light_curve"]
    # )
    psql_db = providers.Dependency(instance_of=SQLConnection)
    mongo_db = providers.Dependency(instance_of=MongoConnection)
    detection_repository_factory = providers.FactoryAggregate(
        {
            "ztf": providers.Factory(PSQLDetectionRepository, db=psql_db),
            "atlas": providers.Factory(MongoDetectionRepository, db=mongo_db),
        }
    )
    non_detection_repository_factory = providers.FactoryAggregate(
        {
            "ztf": providers.Factory(PSQLNonDetectionRepository, db=psql_db),
            "atlas": providers.Factory(
                MongoNonDetectionRepository, db=mongo_db
            ),
        }
    )
    lightcurve_service = providers.Factory(
        LightcurveService,
        detection_repository_factory=detection_repository_factory,
        non_detection_repository_factory=non_detection_repository_factory,
    )
    get_detections_command = providers.Factory(
        GetDetection, service=lightcurve_service
    )
    get_non_detections_command = providers.Factory(
        GetNonDetection, service=lightcurve_service
    )
    get_lightcurve_command = providers.Factory(
        GetLightcurve, service=lightcurve_service
    )
