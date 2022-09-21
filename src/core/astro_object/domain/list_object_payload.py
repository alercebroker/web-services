import math

from shared.utils.queries import MongoPayload, MongoFilterRules


class ListAstroObjectPayload(MongoPayload):
    class ListAstroObjectHelpers(MongoPayload.Helpers):
        @staticmethod
        def query_for_probs(
            classifier, version, class_name, ranking, probability
        ):
            output = {
                "classifier_name": {"$eq": classifier}
                if classifier is not None
                else None,
                "classifier_version": {"$eq": version}
                if version is not None
                else None,
                "class_name": {"$eq": class_name}
                if class_name is not None
                else None,
                "probability": {"$gte": probability}
                if probability is not None
                else None,
                "ranking": {"$eq": ranking} if ranking is not None else None,
            }
            return {
                key: value
                for key, value in output.items()
                if value is not None
            } or None

        @staticmethod
        def query_for_locs(ra, dec, radius):
            return (
                {
                    "$centerSphere": [
                        [ra - 180, dec],
                        math.radians(radius / 3600),
                    ]
                }
                if None not in (ra, dec, radius)
                else None
            )

    filter_rules = {
        "_id": MongoFilterRules(
            ["oid"], "$in", ListAstroObjectHelpers.list_of_str
        ),
        "oid": MongoFilterRules(
            ["oid"], "$in", ListAstroObjectHelpers.list_of_str
        ),
        "firstmjd": MongoFilterRules(
            ["firstmjd"],
            ["$gte", "$lte"],
            ListAstroObjectHelpers.list_of_float,
        ),
        "lastmjd": MongoFilterRules(
            ["lastmjd"], ["$gte", "$lte"], ListAstroObjectHelpers.list_of_float
        ),
        "ndet": MongoFilterRules(
            ["ndet"], ["$gte", "$lte"], ListAstroObjectHelpers.list_of_int
        ),
        "tid": MongoFilterRules(
            ["survey_id"], ["$regex", "$options"], ListAstroObjectHelpers.generate_tid_regex
        ),
        "loc": MongoFilterRules(
            ["ra", "dec", "radius"],
            "$geoWithin",
            ListAstroObjectHelpers.query_for_locs,
        ),
        "probabilities": MongoFilterRules(
            [
                "classifier",
                "classifier_version",
                "class",
                "ranking",
                "probability",
            ],
            "$elemMatch",
            ListAstroObjectHelpers.query_for_probs,
        ),
    }
    paginate_map = {"page": "page", "per_page": "page_size", "count": "count"}
    sort_map = {"key": "order_by", "direction": "order_mode"}
    direction_map = {"ASC": 1, "DESC": -1}

    @property
    def filter(self):
        query = super().filter
        if "_id" in query and "oid" in query:
            aid, oid = query.pop("_id"), query.pop("oid")
            query["$or"] = [{"_id": aid}, {"oid": oid}]
        return query

    def probability_filter(self, variable_as):
        pfilter = self.filter.get("probabilities")
        try:
            pfilter = pfilter.get(self.filter_rules["probabilities"].query_key)
        except AttributeError:
            return
        return {
            "$and": [
                {query: [f"$${variable_as}.{field}", value]}
                for field, cond in pfilter.items()
                for query, value in cond.items()
            ]
        }
