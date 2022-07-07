from dataclasses import dataclass


@dataclass
class MagStatsServicePayload:
    oid: str
    survey_id: str


class MagStatsService:
    def __init__(self, magstats_repository_factory):
        self.magstats_repository_factory = magstats_repository_factory

    def get_magstats(self, payload: MagStatsServicePayload):
        repository = self.magstats_repository_factory()
        return repository.get(payload.oid, payload.survey_id)
