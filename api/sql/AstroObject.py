from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from sqlalchemy import text
from astropy import units
import argparse
from werkzeug.exceptions import NotFound
from ..db import db

api = Namespace("objects", description="Objects related operations")


object_list_item = api.model(
    "ObjectListItem",
    {
        "oid": fields.String(description="Object identifier"),
        "ndet": fields.String(description="Number of detections"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "ra": fields.Float(description="Right Ascention", attribute="meanra"),
        "dec": fields.Float(description="Declination", attribute="meandec"),
        "xmatch_class_catalog": fields.String(description="class in other catalog"),
        "class_name": fields.String(description="ALeRCE's classification"),
        "probability": fields.Float(description="Probability of being <class_name>"),
    },
)
object_item = api.model(
    "Object",
    {
        "oid": fields.String(description="Object identifier"),
        "ndet": fields.String(description="Number of detections"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "ra": fields.Float(description="Right Ascention"),
        "dec": fields.Float(description="Declination"),
    },
)

object_list = api.model(
    "ObjectList",
    {
        "total": fields.Integer(description="Total of objects in query"),
        "page": fields.Integer(description="Current page number"),
        "next": fields.Integer(description="Next page"),
        "has_next": fields.Boolean(description="Whether it has a next page"),
        "prev": fields.Integer(description="Previous page number"),
        "has_prev": fields.Boolean(description="Whether it has previous page"),
        "results": fields.List(fields.Nested(object_list_item)),
    },
)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "classifier",
        type=str,
        dest="classifier",
        location="args",
        help="classifier name",
    )
    parser.add_argument(
        "class", type=str, dest="class", location="args", help="class name"
    )
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
        "ra",
        type=float,
        dest="ra",
        location="args",
        help="Ra in degrees for conesearch.",
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

    @api.doc("list_object")
    @api.expect(parser)
    @api.marshal_with(object_list)
    def get(self):
        """List all objects by given filters"""
        args = self.parser.parse_args()
        params = self.parse_parameters(args)
        conesearch_args = self._parse_conesearch_args(args)
        ret = []
        query = self._get_objects(params, conesearch_args).paginate(
            args["page"], args["page_size"], args["count"]
        )
        for obj, clf in query.items:
            obj = {**obj.__dict__}
            clf = {**clf.__dict__} if clf else {}
            ret.append({**obj, **clf})

        if len(ret):
            return {
                "total": query.total,
                "page": query.page,
                "next": query.next_num,
                "has_next": query.has_next,
                "prev": query.prev_num,
                "has_prev": query.has_prev,
                "results": ret,
            }
        else:
            raise NotFound("Objects not found")

    def _get_objects(self, params, conesearch_args):
        return (
            db.session.query(AstroObject, Classification)
            .outerjoin(AstroObject.classifications)
            .filter(*params)
            .params(**conesearch_args)
        )

    def parse_parameters(self, args):
        classifier, class_, ndet, firstmjd, lastmjd, probability, conesearch = (
            True,
            True,
            True,
            True,
            True,
            True,
            True,
        )
        for arg in args:
            if args[arg] is not None:
                if arg == "classifier":
                    classifier = Classification.classifier_name == args[arg]
                if arg == "class":
                    class_ = Classification.class_name == args[arg]
                if arg == "ndet":
                    ndet = AstroObject.nobs >= args[arg][0]
                    if len(args[arg]) > 1:
                        ndet = ndet & (AstroObject.nobs <= args[arg][1])
                if arg == "firstmjd":
                    firstmjd = AstroObject.firstmjd >= args[arg][0]
                    if len(args[arg]) > 1:
                        firstmjd = firstmjd & (AstroObject.firstmjd <= args[arg][1])
                if arg == "lastmjd":
                    lastmjd = AstroObject.lastmjd >= args[arg][0]
                    if len(args[arg]) > 1:
                        lastmjd = lastmjd & (AstroObject.lastmjd <= args[arg][1])
                if arg == "probability":
                    probability = Classification.probability >= args[arg]
        conesearch = self._create_conesearch_statement(args)
        return classifier, class_, ndet, firstmjd, lastmjd, probability, conesearch

    def _create_conesearch_statement(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args["radius"]
        except KeyError as e:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
        else:
            return True

    def _parse_conesearch_args(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args["radius"]
        except KeyError as e:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            radius = radius * units.arcsec
            radius = radius.to(units.deg)
            radius = radius.value
        return {"ra": ra, "dec": dec, "radius": radius}


@api.route("/<id>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Object not found")
class Object(Resource):
    @api.doc("get_object")
    @api.marshal_with(object_item)
    def get(self, id):
        """Fetch an object given its identifier"""
        result = (
            db.session.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        )
        if result:
            return result
        else:
            raise NotFound("Object not found")
