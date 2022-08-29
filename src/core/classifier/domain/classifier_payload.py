from shared.utils.queries import MongoPayload, MongoFilterRules


class ClassifiersPayload(MongoPayload):
    filter_rules = {
        "classifier_name": MongoFilterRules(["classifier_name"], None, str),
        "classifier_version": MongoFilterRules(
            ["classifier_version"], None, str
        ),
    }

    def __init__(self, classifier_name=None, classifier_version=None):
        super().__init__(
            {
                "classifier_name": classifier_name,
                "classifier_version": classifier_version,
            }
        )
