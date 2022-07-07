from db_plugins.db.mongo import models
from returns.result import Success, Failure
from shared.error.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)


class MongoRepository:
    def _get_object(self, object_id: str, survey_id: str):
        try:
            astro_object = self.db.query().find_one(
                model=models.Object, filter_by={"oid": object_id}
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
