from flask_restx import reqparse
from .models import object_item


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise reqparse.ArgumentTypeError("Boolean value expected.")


filters = reqparse.RequestParser()
filters.add_argument(
    "oid",
    type=str,
    dest="oid",
    location="args",
    help="Object identifier (can be ALeRCE and/or survey identifier)",
    action="append",
)
filters.add_argument(
    "ndet",
    type=int,
    dest="ndet",
    location="args",
    help="One element is minimum number of detections. Second value is maximum",
    action="append",
)
filters.add_argument(
    "firstmjd",
    type=float,
    dest="firstmjd",
    location="args",
    help="One element is the minimum MJD for first detection. Second values is maximum",
    action="append",
)
filters.add_argument(
    "lastmjd",
    type=float,
    dest="lastmjd",
    location="args",
    help="One element is the minimum MJD for last detection. Second values is maximum",
    action="append",
)
filters.add_argument(
    "ra",
    type=float,
    dest="ra",
    location="args",
    help="Right ascension center (in degrees) for conesearch",
)
filters.add_argument(
    "dec",
    type=float,
    dest="dec",
    location="args",
    help="Declination center (in degrees) for conesearch.",
)
filters.add_argument(
    "radius",
    default=30.0,
    type=float,
    dest="radius",
    location="args",
    help="Circle radius in arcseconds for conesearch",
)
filters.add_argument(
    "classifier",
    type=str,
    dest="classifier",
    location="args",
    help="Classifier name",
)
filters.add_argument(
    "classifier_version",
    type=str,
    dest="classifier_version",
    location="args",
    help="Classifier version",
)
filters.add_argument(
    "class",
    type=str,
    dest="class",
    location="args",
    help="Class name",
)
filters.add_argument(
    "ranking",
    type=int,
    dest="ranking",
    location="args",
    help="Class ranking within classifier",
)
filters.add_argument(
    "probability",
    type=float,
    dest="probability",
    location="args",
    help="Minimum probability of belonging to given class",
)

pagination = reqparse.RequestParser()
pagination.add_argument(
    "page",
    default=1,
    type=int,
    dest="page",
    location="args",
    help="Result page to retrieve",
)
pagination.add_argument(
    "page_size",
    default=10,
    type=int,
    dest="page_size",
    location="args",
    help="Number of objects to retrieve in each page",
)
pagination.add_argument(
    "count",
    type=str2bool,
    default=False,
    dest="count",
    location="args",
    help="Whether to count total number of objects",
)

order = reqparse.RequestParser()
order.add_argument(
    "order_by",
    type=str,
    dest="order_by",
    location="args",
    help="Column used for ordering",
    choices=list(object_item),
)
order.add_argument(
    "order_mode",
    type=str,
    dest="order_mode",
    location="args",
    choices=["ASC", "DESC"],
    help="Ordering direction",
)
