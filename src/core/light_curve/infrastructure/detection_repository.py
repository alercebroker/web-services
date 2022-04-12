from db_plugins.db.sql.connection import SQLConnection
from db_plugins.db.mongo.connection import MongoConnection
from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from returns.result import Success, Failure
from returns.pipeline import is_successful
from shared.error.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)
import abc


class DetectionRepository(metaclass=abc.ABCMeta):
    def get(self, object_id):
        raise NotImplementedError()


class PSQLDetectionRepository(DetectionRepository):
    def __init__(self, db: SQLConnection):
        self.db = db

    def _get_object_by_id(self, object_id: str, survey_id: str):
        try:
            query_result = (
                self.db.query(psql_models.Object)
                .filter(psql_models.Object.oid == object_id)
                .one_or_none()
            )

            if query_result:
                return Success(query_result)
            else:
                return Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=survey_id
                        )
                    )
                )
        except Exception as e:
            return Failure(ServerErrorException(e))

    def get(self, object_id, survey_id):
        astro_obj = self._get_object_by_id(object_id, survey_id)

        if is_successful(astro_obj):
            detections = astro_obj.unwrap().detections
            return Success(detections)
        else:
            return astro_obj


class MongoDetectionRepository(DetectionRepository):
    def __init__(self, db: MongoConnection):
        self.db = db

    def _get_object(self, object_id, survey_id):
        try:
            astro_object = self.db.query().find_one(
                model=mongo_models.Object, filter_by={"oid": object_id}
            )
            if astro_object:
                return Success(astro_object)
            else:
                return Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=survey_id
                        )
                    )
                )
        except Exception as e:
            return Failure(ServerErrorException(e))

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
            aid = astro_object.unwrap()["aid"]
            detections = self._get_detections(aid)

            if is_successful(detections) and len(detections.unwrap()) > 0:
                return detections
            else:
                raise Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=self.survey_id
                        )
                    )
                )
        else:
            return astro_object
