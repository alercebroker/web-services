from db_plugins.db.mongo.connection import MongoConnection
from dependency_injector import containers, providers

from . import infrastructure, use_case
from .domain import ProbabilitiesService


class ProbabilitiesContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_probabilities = providers.Factory(
        infrastructure.ProbabilitiesRepository, db=db
    )

    service = providers.Factory(
        ProbabilitiesService, repo_probabilities=repo_probabilities
    )
    get_probabilities = providers.Factory(
        use_case.GetProbabilities, service=service
    )
