from flask_restx import reqparse

SURVEY_ID_CHOICES = ["ztf", "atlas"]

survey_id_parser = reqparse.RequestParser()
survey_id_parser.add_argument(
    "survey_id",
    type=str,
    dest="survey_id",
    location="args",
    help="Survey identifier",
    choices=SURVEY_ID_CHOICES,
)
