from dataclasses import dataclass


@dataclass
class MagStatsServicePayload:
    oid: str
    survey_id: str


class MagStatsService:
    def __init__(self, repository):
        self.repository = repository

    def get_magstats(self, payload: MagStatsServicePayload):
        return self.repository.get(payload.oid, payload.survey_id)
