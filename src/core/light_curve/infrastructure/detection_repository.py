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


class DetectionRepository:
    def get(self, object_id, survey_id):
        raise NotImplementedError()


class PSQLDetectionRepository(DetectionRepository, PSQLRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager]):
        self.session_factory = session_factory

    def get(self, object_id, survey_id):
        detections = self._get_detections_by_oid(object_id, survey_id)

        if is_successful(detections):
            detections = detections.unwrap()
            return Success(detections)
        else:
            return detections


class MongoDetectionRepository(DetectionRepository, MongoRepository):
    def __init__(self, db: MongoConnection):
        self.db = db

    def _get_detections(self, object_id):
        try:
            detections = self.db.query().find_all(
                model=mongo_models.Detection,
                filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
                paginate=False,
            )

            return Success(list(detections))
        except Exception as e:
            return Failure(ServerErrorException(e))

    def get(self, object_id, survey_id):
        astro_object = self._get_object(object_id, survey_id)

        if is_successful(astro_object):
            aid = astro_object.unwrap()["_id"]
            detections = self._get_detections(aid)

            if is_successful(detections) and len(detections.unwrap()) > 0:
                return detections
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
