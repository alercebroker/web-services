from flask_restx import reqparse

fid_parser = reqparse.RequestParser()
fid_parser.add_argument(
    "fid",
    type=int,
    help="Feture fid name",
)
