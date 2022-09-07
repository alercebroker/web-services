from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import ListAstroObjectPayload


class ListAstroObjectRepository(MongoRepository):
    def _query(self, payload: ListAstroObjectPayload):
        variable_as = "item"  # Used as alias when filtering by probabilities
        fields = (
            "aid",
            "ndet",
            "firstmjd",
            "lastmjd",
            "meanra",
            "meandec",
            "probabilities",
        )
        probabilities = (
            "classifier_name",
            "classifier_version",
            "class_name",
            "probability",
            "ranking",
        )

        pipe = [
            {"$match": payload.filter},
            {"$project": {field: True for field in fields}},
        ]
        probability_filter = payload.probability_filter(variable_as)
        if probability_filter:
            pipe[-1]["$project"].update(
                {
                    "probabilities": {
                        "$filter": {
                            "input": "$probabilities",
                            "as": variable_as,
                            "cond": probability_filter,
                        }
                    }
                }
            )
        pipe.append(
            {
                "$unwind": {
                    "path": "$probabilities",
                    "preserveNullAndEmptyArrays": True,
                }
            }
        )
        pipe.append(
            {
                "$addFields": {
                    field: f"$probabilities.{field}" for field in probabilities
                }
            }
        )
        pipe.append({"$project": {"probabilities": 0}})
        if payload.sort:
            pipe.append({"$sort": payload.sort})

        paginate = True if payload.paginate else False
        return self.db.query().find_all(
            model=models.Object,
            filter_by=pipe,
            paginate=paginate,
            **payload.paginate,
        )

    def _wrap_results(self, result):
        # There is no failure if query is empty in this case
        result = {
            "total": result.total,
            "page": result.page,
            "next": result.next_num,
            "has_next": result.has_next,
            "prev": result.prev_num,
            "has_prev": result.has_prev,
            "items": result.items,
        }
        return Success(result)
