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
    "Object List Item",
    {
        "oid": fields.String(description="Object identifier"),
        "ndethist": fields.String(
            description="Number of spatially-coincident detections falling within 1.5 arcsec going back to beginning of survey; only detections that fell on the same field and readout-channel ID where the input candidate was observed are counted. All raw detections down to a photometric S/N of ~ 3 are included."
        ),
        "ncovhist": fields.Integer(
            description="Number of times input candidate position fell on any field and readout-channel going back to beginning of survey"
        ),
        "jdstarthist": fields.Float(
            description="Earliest Julian date of epoch corresponding to ndethist [days]"
        ),
        "jdendhist": fields.Float(
            description="Latest Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(description="total number of detections for the object"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "deltamjd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(description="right ascension standard deviation"),
        "sigmadec": fields.Float(description="declination standard deviation"),
        "class": fields.String(description="Highest probability class"),
        "probability": fields.Float(description="Highest probability")
    },
)
object_item = api.model(
    "Single Object",
    {
        "oid": fields.String(description="Object identifier"),
        "ndethist": fields.String(
            description="Number of spatially-coincident detections falling within 1.5 arcsec going back to beginning of survey; only detections that fell on the same field and readout-channel ID where the input candidate was observed are counted. All raw detections down to a photometric S/N of ~ 3 are included."
        ),
        "ncovhist": fields.Integer(
            description="Number of times input candidate position fell on any field and readout-channel going back to beginning of survey"
        ),
        "jdstarthist": fields.Float(
            description="Earliest Julian date of epoch corresponding to ndethist [days]"
        ),
        "jdendhist": fields.Float(
            description="Latest Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(description="total number of detections for the object"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "deltamjd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(description="right ascension standard deviation"),
        "sigmadec": fields.Float(descriptin="declination standard deviation"),
    },
)

object_list = api.model(
    "Paginated Object List",
    {
        "total": fields.Integer(description="Total of objects in query"),
        "page": fields.Integer(description="Current page number"),
        "next": fields.Integer(description="Next page"),
        "has_next": fields.Boolean(description="Whether it has a next page"),
        "prev": fields.Integer(description="Previous page number"),
        "has_prev": fields.Boolean(description="Whether it has previous page"),
        "items": fields.List(fields.Nested(object_list_item)),
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
        page = self._get_objects(params, conesearch_args).paginate(
            args["page"], args["page_size"], args["count"]
        )
        for obj, clf in page.items:
            obj = {**obj.__dict__}
            clf = {**clf.__dict__} if clf else {}
            ret.append({**obj, **clf})

        if len(ret):
            return {
                "total": page.total,
                "page": page.page,
                "next": page.next_num,
                "has_next": page.has_next,
                "prev": page.prev_num,
                "has_prev": page.has_prev,
                "items": ret,
            }
        else:
            raise NotFound("Objects not found")

    def _get_objects(self, params, conesearch_args):
        return (
            db.query(AstroObject, Classification)
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
            db.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        )
        if result:
            return result
        else:
            raise NotFound("Object not found")
