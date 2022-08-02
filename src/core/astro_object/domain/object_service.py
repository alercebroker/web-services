import math

from shared.utils.queries import MongoPayload, MongoFilterRules


class AstroObjectPayload(MongoPayload):
    class AstroObjectHelpers(MongoPayload.Helpers):
        @staticmethod
        def query_for_locs(ra, dec, radius):
            return {
                "$centerSphere": [[ra - 180, dec], math.radians(radius / 3600)]
            }

        @staticmethod
        def filter_aid(arg):
            return [
                aid
                for aid in MongoPayload.Helpers.list_of_str(arg)
                if aid.startswith("AL")
            ] or None

        @staticmethod
        def filter_oid(arg):
            return [
                oid
                for oid in MongoPayload.Helpers.list_of_str(arg)
                if not oid.startswith("AL")
            ] or None

    filter_rules = {
        "aid": MongoFilterRules(["oid"], "$in", AstroObjectHelpers.filter_aid),
        "oid": MongoFilterRules(["oid"], "$in", AstroObjectHelpers.filter_oid),
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


class AstroObjectService:
    def __init__(self, repo_list_object, repo_single_object, repo_limits):
        self.repo_list_object = repo_list_object
        self.repo_single_object = repo_single_object
        self.repo_limits = repo_limits

    def get_list_object(self, payload: AstroObjectPayload):
        return self.repo_list_object.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.repo_single_object.get(payload)

    def get_limits(self, payload: AstroObjectPayload):
        return self.repo_limits.get(payload)
