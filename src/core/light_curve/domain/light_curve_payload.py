from shared.utils.queries import MongoPayload, MongoFilterRules


class LightCurvePayload(MongoPayload):
    filter_rules = {
        "aid": MongoFilterRules(["aid"], None, str),
        "tid": MongoFilterRules(
            ["survey_id"],
            ["$regex", "$options"],
            MongoPayload.Helpers.generate_tid_regex,
        ),
    }
    paginate_map = {"page": "page", "per_page": "page_size"}
    sort_map = {"key": "order_by", "direction": "order_mode"}
    direction_map = {"ASC": 1, "DESC": -1}

    def __init__(self, aid, filter_args, paginate_args=None, sort_args=None):
        super().__init__({"aid": aid, **filter_args}, paginate_args, sort_args)
