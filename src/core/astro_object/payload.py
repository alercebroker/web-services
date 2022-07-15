import math

from shared.utils.queries import MongoPayload, MongoFilterRules


class AstroObjectPayload(MongoPayload):
    class AstroObjectHelpers(MongoPayload.Helpers):
        @staticmethod
        def query_for_locs(ra, dec, radius):
            return {
                "$centerSphere": [[ra - 180, dec], math.radians(radius / 3600)]
            }

    filter_rules = {
        "aid": MongoFilterRules(
            ["aid"], "$in", AstroObjectHelpers.list_of_str
        ),
        "oid": MongoFilterRules(
            ["oid"], "$in", AstroObjectHelpers.list_of_str
        ),
        "firstmjd": MongoFilterRules(
            ["firstmjd"], ["$gte", "$lte"], AstroObjectHelpers.list_of_float
        ),
        "lastmjd": MongoFilterRules(
            ["lastmjd"], ["$gte", "$lte"], AstroObjectHelpers.list_of_float
        ),
        "ndet": MongoFilterRules(
            ["ndet"], ["$gte", "$lte"], AstroObjectHelpers.list_of_int
        ),
        "loc": MongoFilterRules(
            ["ra", "dec", "radius"],
            "$geoWithin",
            AstroObjectHelpers.query_for_locs,
        ),
    }
    paginate_map = {"page": "page", "per_page": "page_size", "count": "count"}
    sort_map = {"key": "order_by", "direction": "order_mode"}
    direction_map = {"ASC": 1, "DESC": -1}
