from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from returns.result import Success, Failure

from ..result_handlers.helper_functions import (
    is_failure,
    is_success,
    get_failure_from_list,
)
from .psql_db import db as psql_db
from .mongo_db import db as mongo_db
from ..result_handlers.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)


class DBInterface(object):
    @classmethod
    def get_interface_query(cls, query_name):
        return getattr(cls, query_name)

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
        try:
            query_result = (
                psql_db.query(psql_models.Object)
                .filter(psql_models.Object.oid == object_id)
                .one_or_none()
            )

            if query_result:
                return Success(query_result)
            else:
                return Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=cls.survey_id
                        )
                    )
                )
        except Exception as e:
            return Failure(ServerErrorException(e))

    @classmethod
    def get_light_curve(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        if is_success(astro_obj):
            light_curve = astro_obj.unwrap().get_lightcurve()
            for det in light_curve["detections"]:
                det.phase = 0  # (det.mjd % obj.period) / obj.period
            return Success(light_curve)
        else:
            return astro_obj

    @classmethod
    def get_detections(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        if is_success(astro_obj):
            detections = astro_obj.unwrap().detections
            return Success(detections)
        else:
            return astro_obj

    @classmethod
    def get_non_detections(cls, object_id):
        astro_obj = cls._get_object_by_id(object_id)

        if is_success(astro_obj):
            non_detections = astro_obj.unwrap().non_detections
            return Success(non_detections)
        else:
            return astro_obj


class MongoInterface(DBInterface):
    survey_id = "atlas"

    @classmethod
    def _get_object(cls, object_id):
        try:
            astro_object = mongo_db.query().find_one(
                model=mongo_models.Object, filter_by={"oid": object_id}
            )
            if astro_object:
                return Success(astro_object)
            else:
                return Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=cls.survey_id
                        )
                    )
                )
        except Exception as e:
            return Failure(ServerErrorException(e))

    @classmethod
    def _get_detections(cls, object_id):
        try:
            detections = mongo_db.query().find_all(
                model=mongo_models.Detection,
                filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
                paginate=False,
            )

            return Success(list(detections))
        except Exception as e:
            return Failure(ServerErrorException(e))

    @classmethod
    def _get_non_detections(cls, object_id):
        try:
            non_detections = mongo_db.query().find_all(
                model=mongo_models.NonDetection,
                filter_by={"aid": object_id, "tid": {"$regex": "ATLAS*"}},
                paginate=False,
            )
            return Success(list(non_detections))
        except Exception as e:
            return Failure(ServerErrorException(e))

    @classmethod
    def get_light_curve(cls, object_id):
        astro_object = cls._get_object(object_id)

        if is_success(astro_object):
            aid = astro_object.unwrap()["aid"]
            light_curve_data = [
                cls._get_detections(aid),
                cls._get_non_detections(aid),
            ]
            failure_found = get_failure_from_list(
                results_list=light_curve_data
            )

            if failure_found:
                return failure_found
            else:
                light_curve = {
                    "detections": light_curve_data[0].unwrap(),
                    "non_detections": light_curve_data[1].unwrap(),
                }

                for det in light_curve["detections"]:
                    det["phase"] = 0  # (det.mjd % obj.period) / obj.period

                return Success(light_curve)
        else:
            return astro_object

    @classmethod
    def get_detections(cls, object_id):
        astro_object = cls._get_object(object_id)

        if is_success(astro_object):
            aid = astro_object.unwrap()["aid"]
            detections = cls._get_detections(aid)

            if is_success(detections) and len(detections.unwrap()) > 0:
                return detections
            else:
                raise Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=cls.survey_id
                        )
                    )
                )
        else:
            return astro_object

    @classmethod
    def get_non_detections(cls, object_id):
        astro_object = cls._get_object(object_id)

        if is_success(astro_object):
            aid = astro_object.unwrap()["aid"]
            non_detections = cls._get_non_detections(aid)

            if is_success(non_detections) and len(non_detections.unwrap()) > 0:
                return non_detections
            else:
                raise Failure(
                    ClientErrorException(
                        ObjectNotFound(
                            object_id=object_id, survey_id=cls.survey_id
                        )
                    )
                )
        else:
            return astro_object
