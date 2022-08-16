from db_plugins.db.mongo.connection import MongoConnection
from dependency_injector import containers, providers

from . import infrastructure, use_case
from .domain import FeaturesService


class FeaturesContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_features = providers.Factory(infrastructure.FeaturesRepository, db=db)

    service = providers.Factory(FeaturesService, repo_features=repo_features)
    get_features = providers.Factory(use_case.GetFeatures, service=service)
