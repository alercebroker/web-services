from dependency_injector import containers, providers
from .infrastructure.magstats_repository import MongoMagStatsRepository
from .domain.magstats_service import MagStatsService
from .use_case.get_magstats import GetMagStats
from db_plugins.db.mongo.connection import MongoConnection


class MagStatsContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)
    repository = providers.Factory(MongoMagStatsRepository, db=db)

    service = providers.Factory(MagStatsService, repository=repository)
    command = providers.Factory(GetMagStats, service=service)
