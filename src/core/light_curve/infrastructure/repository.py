from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from returns.result import Success, Failure
from shared.error.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)


class PSQLRepository:
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


class MongoRepository:
    def _get_object(self, object_id: str, survey_id: str):
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
