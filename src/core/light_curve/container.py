from db_plugins.db.mongo.connection import MongoConnection
from dependency_injector import containers, providers
from .infrastructure import (
    DetectionRepository,
    NonDetectionRepository,
    LightCurveRepository,
)
from .domain import LightCurveService
from .use_case import GetDetections, GetNonDetections, GetLightCurve


class LightcurveContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_detections = providers.Factory(DetectionRepository, db=db)
    repo_non_detections = providers.Factory(NonDetectionRepository, db=db)
    repo_lightcurve = providers.Factory(LightCurveRepository, db=db)

    service = providers.Factory(
        LightCurveService,
        repo_detections=repo_detections,
        repo_non_detections=repo_non_detections,
        repo_lightcurve=repo_lightcurve
    )
    get_detections = providers.Factory(GetDetections, service=service)
    get_non_detections = providers.Factory(GetNonDetections, service=service)
    get_lightcurve = providers.Factory(GetLightCurve, service=service)
