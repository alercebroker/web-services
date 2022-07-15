from shared.utils.queries import MongoPayload, MongoFilterRules


class LightCurvePayload(MongoPayload):
    class LightCurveHelpers(MongoPayload.Helpers):
        @staticmethod
        def generate_tid_regex(string):
            return f"{string.upper()}*"

    filter_rules = {
        "aid": MongoFilterRules(
            ["oid"], "$in", LightCurveHelpers.list_of_str
        ),
        "oid": MongoFilterRules(
            ["tid"], "$regex", LightCurveHelpers.generate_tid_regex
        ),
    }
