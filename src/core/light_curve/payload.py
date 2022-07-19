from shared.utils.queries import MongoPayload, MongoFilterRules


class LightCurvePayload(MongoPayload):
    class LightCurveHelpers(MongoPayload.Helpers):
        @staticmethod
        def generate_tid_regex(string):
            return f"{string}.*", "i"

    filter_rules = {
        "aid": MongoFilterRules(["aid"], None, str),
        "tid": MongoFilterRules(
            ["survey_id"], ["$regex", "$options"], LightCurveHelpers.generate_tid_regex
        ),
    }