from flask_restx import reqparse
from db_plugins.db.sql import models

columns = []
for c in models.Object.__table__.columns:
    columns.append(str(c).split(".")[1])
for c in models.Probability.__table__.columns:
    columns.append(str(c).split(".")[1])


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise reqparse.ArgumentTypeError("Boolean value expected.")


def create_parsers():
    filter_parser = reqparse.RequestParser()
    filter_parser.add_argument(
        "oid",
        type=str,
        dest="oid",
        location="args",
        help="Object id",
        action="append",
    )
    filter_parser.add_argument(
        "ndet",
        type=int,
        dest="ndet",
        location="args",
        help="Range of detections.",
        action="append",
    )
    filter_parser.add_argument(
        "firstmjd",
        type=float,
        dest="firstmjd",
        location="args",
        help="First detection date range in mjd.",
        action="append",
    )
    filter_parser.add_argument(
        "lastmjd",
        type=float,
        dest="lastmjd",
        location="args",
        help="Last detection date range in mjd.",
        action="append",
    )
    filter_parser.add_argument(
        "ra",
        type=float,
        dest="ra",
        location="args",
        help="Ra in degrees for conesearch.",
    )
    filter_parser.add_argument(
        "dec",
        type=float,
        dest="dec",
        location="args",
        help="Dec in degrees for conesearch.",
    )
    filter_parser.add_argument(
        "radius",
        default=30.,
        type=float,
        dest="radius",
        location="args",
        help="Radius in arcsec for conesearch. (Default: 30 arcsec)",
    )

    pagination_parser = reqparse.RequestParser()
    pagination_parser.add_argument(
        "page",
        default=1,
        type=int,
        dest="page",
        location="args",
        help="Page or offset to retrieve.",
    )
    pagination_parser.add_argument(
        "page_size",
        default=10,
        type=int,
        dest="page_size",
        location="args",
        help="Number of objects to retrieve in each page.",
    )
    pagination_parser.add_argument(
        "count",
        type=str2bool,
        default=False,
        dest="count",
        location="args",
        help="Whether to count total objects or not.",
    )

    order_parser = reqparse.RequestParser()
    order_parser.add_argument(
        "order_by",
        type=str,
        dest="order_by",
        location="args",
        help="Column used for ordering",
        choices=columns,
    )
    order_parser.add_argument(
        "order_mode",
        type=str,
        dest="order_mode",
        location="args",
        choices=["ASC", "DESC"],
        help="Order could be ascending or descending",
    )

    return filter_parser, order_parser, pagination_parser
