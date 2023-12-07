from db_plugins.db.mongo.connection import MongoConnection
from db_plugins.db.mongo import models as mongo_models
from returns.result import Success, Failure
from returns.pipeline import is_successful
from shared.error.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)
from core.light_curve.infrastructure.repository import (
    PSQLRepository,
    MongoRepository,
)
from contextlib import AbstractContextManager
from typing import Callable


class NonDetectionRepository:
    def get(self, object_id, survey_id):
        raise NotImplementedError()


class PSQLNonDetectionRepository(NonDetectionRepository, PSQLRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager]):
        self.session_factory = session_factory

    def get(self, object_id, survey_id):
        non_detections = self._get_non_detections_by_oid(object_id, survey_id)

        if is_successful(non_detections):
            non_detections = non_detections.unwrap()
            return Success(non_detections)
        else:
            return non_detections


class MongoNonDetectionRepository(NonDetectionRepository, MongoRepository):
    def __init__(self, db: MongoConnection):
        self.db = db

    def _get_non_detections(self, object_id):
        try:
            non_detections = self.db.query().find_all(
                model=mongo_models.NonDetection,
                filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
                paginate=False,
            )
            return Success(list(non_detections))
        except Exception as e:
            return Failure(ServerErrorException(e))

    def get(self, object_id, survey_id):
        astro_object = self._get_object(object_id, survey_id)

        if is_successful(astro_object):
            aid = astro_object.unwrap()["_id"]
            non_detections = self._get_non_detections(aid)

            if is_successful(non_detections):
                return non_detections
            else:
                return Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=survey_id
                        )
                    )
                )
        else:
            return astro_object
