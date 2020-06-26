from flask_restx import reqparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


parser = reqparse.RequestParser()
parser.add_argument(
    "classifier", type=str, dest="classifier", location="args", help="classifier name",
)
parser.add_argument("class", type=str, dest="class", location="args", help="class name")
parser.add_argument(
    "ndet",
    type=int,
    dest="ndet",
    location="args",
    help="Range of detections.",
    action="append",
)
parser.add_argument(
    "probability",
    type=float,
    dest="probability",
    location="args",
    help="Minimum probability.",
)
parser.add_argument(
    "firstmjd",
    type=float,
    dest="firstmjd",
    location="args",
    help="First detection date range in mjd.",
    action="append",
)
parser.add_argument(
    "lastmjd",
    type=float,
    dest="lastmjd",
    location="args",
    help="Last detection date range in mjd.",
    action="append",
)
parser.add_argument(
    "ra", type=float, dest="ra", location="args", help="Ra in degrees for conesearch.",
)
parser.add_argument(
    "dec",
    type=float,
    dest="dec",
    location="args",
    help="Dec in degrees for conesearch.",
)
parser.add_argument(
    "radius",
    type=float,
    dest="radius",
    location="args",
    help="Radius in arcsec for conesearch.",
)
parser.add_argument(
    "page",
    default=1,
    type=int,
    dest="page",
    location="args",
    help="Page or offset to retrieve.",
)
parser.add_argument(
    "page_size",
    default=10,
    type=int,
    dest="page_size",
    location="args",
    help="Number of objects to retrieve in each page.",
)
parser.add_argument(
    "count",
    type=str2bool,
    default=True,
    dest="count",
    location="args",
    help="Whether to count total objects or not.",
)
