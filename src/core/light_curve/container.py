from db_plugins.db.mongo.connection import MongoConnection
from dependency_injector import containers, providers

from . import infrastructure, use_case
from .domain import LightCurveService


class LightCurveContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_detections = providers.Factory(
        infrastructure.DetectionRepository, db=db
    )
    repo_non_detections = providers.Factory(
        infrastructure.NonDetectionRepository, db=db
    )
    repo_lightcurve = providers.Factory(
        infrastructure.LightCurveRepository, db=db
    )

    service = providers.Factory(
        LightCurveService,
        repo_detections=repo_detections,
        repo_non_detections=repo_non_detections,
        repo_lightcurve=repo_lightcurve,
    )
    get_detections = providers.Factory(use_case.GetDetections, service=service)
    get_non_detections = providers.Factory(
        use_case.GetNonDetections, service=service
    )
    get_lightcurve = providers.Factory(use_case.GetLightCurve, service=service)
