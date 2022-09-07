from flask_restx import reqparse

filters = reqparse.RequestParser()
filters.add_argument(
    "classifier", type=str, location="args", help="Classifier name"
)
filters.add_argument(
    "classifier_version", type=str, location="args", help="Classifier version"
)
