from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from .psql_db import db as psql_db
from .mongo_db import db as mongo_db


class ObjectNotFound(Exception):
    """
    Exception for empty queries for object data.
    Revelevan for any api with the object/<id> path.

    Attributes:
      object_id : the id of the object searched
      survey_id : the id of the survey in wich the oid was searched
    """

    def __init__(self, object_id, survey_id) -> None:
        super().__init__()
        self.object_id = object_id
        self.survey_id = survey_id

    def __str__(self) -> str:
        return f"Object {self.object_id} Not Found in survey {self.survey_id}"


class DBInterface(object):
    @classmethod
    def get_light_curve(cls, object_id):
        raise NotImplementedError()

    @classmethod
    def get_detections(cls, object_id):
        raise NotImplementedError()

    @classmethod
    def get_non_detections(cls, object_id):
        raise NotImplementedError()


class PSQLInterface(DBInterface):
    survey_id = "ztf"

    @classmethod
    def _get_object_by_id(cls, object_id):
        query_result = (
            psql_db.query(psql_models.Object)
            .filter(psql_models.Object.oid == object_id)
            .one_or_none()
        )

        if query_result:
            return query_result
        else:
            raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)

    @classmethod
    def get_light_curve(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        light_curve = astro_obj.get_lightcurve()
        for det in light_curve["detections"]:
            det.phase = 0  # (det.mjd % obj.period) / obj.period

        return light_curve

    @classmethod
    def get_detections(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        return astro_obj.detections

    @classmethod
    def get_non_detections(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        return astro_obj.non_detections


class MongoInterface(DBInterface):
    survey_id = "atlas"

    @classmethod
    def _get_object(cls, object_id):
        astro_object = mongo_db.query().find_one(
            model=mongo_models.Object, filter_by={"oid": object_id}
        )
        if astro_object:
            return astro_object
        else:
            raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)

    @classmethod
    def _get_detections(cls, object_id):
        detections = mongo_db.query().find_all(
            model=mongo_models.Detection,
            filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
            paginate=False,
        )

        return list(detections)

    @classmethod
    def _get_non_detections(cls, object_id):
        non_detections = mongo_db.query().find_all(
            model=mongo_models.NonDetection,
            filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
            paginate=False,
        )

        return list(non_detections)

    @classmethod
    def get_light_curve(cls, object_id):
        astro_object = cls._get_object(object_id)
        aid = astro_object["aid"]

        light_curve = {
            "detections": cls._get_detections(aid),
            "non_detections": cls._get_non_detections(aid),
        }

        for det in light_curve["detections"]:
            det["phase"] = 0  # (det.mjd % obj.period) / obj.period

        return light_curve

    @classmethod
    def get_detections(cls, object_id):
        astro_object = cls._get_object(object_id)
        aid = astro_object["aid"]

        detections = cls._get_detections(aid)

        if detections and len(detections) > 0:
            return detections
        else:
            raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)

    @classmethod
    def get_non_detections(cls, object_id):
        astro_object = cls._get_object(object_id)
        aid = astro_object["aid"]

        non_detections = cls._get_non_detections(aid)

        if non_detections and len(non_detections) > 0:
            return non_detections
        else:
            raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)
