from flask_restx import reqparse

filters = reqparse.RequestParser()
filters.add_argument(
    "fid",
    type=int,
    help="Filter ID",
    location="args",
)
filters.add_argument(
    "version",
    type=str,
    help="Feature version",
    location="args",
)
