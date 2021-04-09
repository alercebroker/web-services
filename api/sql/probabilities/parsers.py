from flask_restx import reqparse

prob_parser = reqparse.RequestParser()
prob_parser.add_argument(
    "classifier", type=str, location="args", help="classifier name"
)
prob_parser.add_argument(
    "classifier_version", type=str, location="args", help="classifier version"
)
