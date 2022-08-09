from shared.utils.queries import MongoPayload, MongoFilterRules


class LightCurvePayload(MongoPayload):
    class LightCurveHelpers(MongoPayload.Helpers):
        @staticmethod
        def generate_tid_regex(string):
            return f"{string}.*", "i"

    filter_rules = {
        "aid": MongoFilterRules(["aid"], None, str),
        "tid": MongoFilterRules(
            ["survey_id"],
            ["$regex", "$options"],
            LightCurveHelpers.generate_tid_regex,
        ),
        "mjd": MongoFilterRules(["mjd"], ["$gte", "$lte"], LightCurveHelpers.list_of_float)
    }
    paginate_map = {"page": "page", "per_page": "page_size", "count": "count"}
    sort_map = {"key": "order_by", "direction": "order_mode"}
    direction_map = {"ASC": 1, "DESC": -1}
