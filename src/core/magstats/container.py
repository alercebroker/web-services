from db_plugins.db.mongo.connection import MongoConnection
from dependency_injector import containers, providers

from . import infrastructure, use_case
from .domain import MagStatsService


class MagStatsContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)
    repo_magstats = providers.Factory(infrastructure.MagStatsRepository, db=db)

    service = providers.Factory(MagStatsService, repo_magstats=repo_magstats)
    command = providers.Factory(use_case.GetMagStats, service=service)
