from flask_restx import reqparse
from .models import object_item
from ..light_curve.parsers import SURVEY_ID_CHOICES


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
    location="args",
    help="Object identifier (can be ALeRCE and/or survey identifier)",
    action="append",
)
filters.add_argument(
    "survey_id",
    type=str,
    location="args",
    help="Survey identifier",
    choices=SURVEY_ID_CHOICES,
)
filters.add_argument(
    "ndet",
    type=int,
    location="args",
    help="One element is minimum number of detections. Second value is maximum",
    action="append",
)
filters.add_argument(
    "firstmjd",
    type=float,
    location="args",
    help="One element is the minimum MJD for first detection. Second values is maximum",
    action="append",
)
filters.add_argument(
    "lastmjd",
    type=float,
    location="args",
    help="One element is the minimum MJD for last detection. Second values is maximum",
    action="append",
)
filters.add_argument(
    "ra",
    type=float,
    location="args",
    help="Right ascension center (in degrees) for conesearch",
)
filters.add_argument(
    "dec",
    type=float,
    location="args",
    help="Declination center (in degrees) for conesearch.",
)
filters.add_argument(
    "radius",
    default=30.0,
    type=float,
    location="args",
    help="Circle radius in arcseconds for conesearch",
)
filters.add_argument(
    "classifier",
    type=str,
    location="args",
    help="Classifier name",
)
filters.add_argument(
    "classifier_version",
    type=str,
    location="args",
    help="Classifier version",
)
filters.add_argument(
    "class",
    type=str,
    location="args",
    help="Class name",
)
filters.add_argument(
    "ranking",
    type=int,
    location="args",
    help="Class ranking within classifier",
)
filters.add_argument(
    "probability",
    type=float,
    location="args",
    help="Minimum probability of belonging to given class",
)

pagination = reqparse.RequestParser()
pagination.add_argument(
    "page",
    default=1,
    type=int,
    location="args",
    help="Result page to retrieve",
)
pagination.add_argument(
    "page_size",
    default=10,
    type=int,
    location="args",
    help="Number of objects to retrieve in each page",
)
pagination.add_argument(
    "count",
    type=str2bool,
    default=False,
    location="args",
    help="Whether to count total number of objects",
)

order = reqparse.RequestParser()
order.add_argument(
    "order_by",
    type=str,
    location="args",
    help="Column used for ordering",
    choices=list(object_item),
)
order.add_argument(
    "order_mode",
    type=str,
    location="args",
    choices=["ASC", "DESC"],
    help="Ordering direction",
)
