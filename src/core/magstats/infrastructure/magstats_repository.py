from db_plugins.db.mongo.connection import MongoConnection
from returns.result import Success
from returns.pipeline import is_successful

from .repository import MongoRepository


class MongoMagStatsRepository(MongoRepository):
    def __init__(self, db: MongoConnection):
        self.db = db

    def get(self, object_id, survey_id):
        result = self._get_object(object_id, survey_id)
        if is_successful(result):
            return Success(result.unwrap()["magstats"])
        return result
