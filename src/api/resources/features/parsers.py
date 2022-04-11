from flask_restx import reqparse

fid_parser = reqparse.RequestParser()
fid_parser.add_argument(
    "fid",
    type=int,
    help="Feature fid number",
    location="args",
)
fid_parser.add_argument(
    "version",
    type=str,
    help="Feature version",
    location="args",
)
