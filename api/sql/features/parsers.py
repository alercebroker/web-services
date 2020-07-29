from flask_restx import reqparse

fid_parser = reqparse.RequestParser()
fid_parser.add_argument(
    "fid",
    type=int,
    help="Feture fid name",
)
fid_parser.add_argument(
    "version",
    type=str,
    help="Feture version",
)
