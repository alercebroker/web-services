from shared.utils.queries import MongoPayload, MongoFilterRules


class LightCurvePayload(MongoPayload):
    class LightCurveHelpers(MongoPayload.Helpers):
        @staticmethod
        def generate_tid_regex(string):
            return f"{string.upper()}*"

    filter_rules = {
        "aid": MongoFilterRules(["aid"], None, str),
        "oid": MongoFilterRules(
            ["survey_id"], "$regex", LightCurveHelpers.generate_tid_regex
        ),
    }
