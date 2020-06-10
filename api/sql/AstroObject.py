from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from ..db import db
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from werkzeug.exceptions import NotFound

api = Namespace("objects", description="Objects related operations")

object_list_model = api.model(
    "ObjectList",
    {
        "oid": fields.String(description="Object identifier"),
        "ndet": fields.String(description="Number of detections"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "ra": fields.Float(description="Right Ascention"),
        "dec": fields.Float(description="Declination"),
        "xmatch_class_catalog": fields.String(description="class in other catalog"),
        "class_name": fields.String(description="ALeRCE's classification"),
        "probability": fields.Float(description="Probability of being <class_name>"),
    },
)
object_model = api.model(
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
        "ndet_min",
        type=int,
        dest="ndet_min",
        location="args",
        help="minimum number of detections",
    )
    parser.add_argument(
        "probability",
        type=float,
        dest="probability",
        location="args",
        help="minimum probability",
    )
    parser.add_argument(
        "mjd",
        type=float,
        dest="mjd",
        location="args",
        help="first detection date exactly or after this date",
    )
    parser.add_argument(
        "page",
        default=1,
        type=int,
        dest="page",
        location="args",
        help="page or offset to retrieve",
    )
    parser.add_argument(
        "page_size",
        default=10,
        type=int,
        dest="page_size",
        location="args",
        help="number of objects to retrieve in each page",
    )

    @api.doc("list_object")
    @api.expect(parser)
    @api.marshal_list_with(object_list_model)
    def get(self):
        """List all objects by given filters"""
        args = self.parser.parse_args()
        params = self.parse_parameters(args)
        ret = []
        for obj, clf in (
            db.session.query(AstroObject, Classification)
            .join(Classification)
            .filter(*params)
            .limit(args["page_size"])
            .offset((args["page"] - 1) * args["page_size"])
            .all()
        ):
            ret.append({**obj.__dict__, **clf.__dict__})

        if len(ret):
            return ret
        else:
            raise NotFound("Objects not found")

    def parse_parameters(self, args):
        classifier, class_, ndet_min, mjd, probability = True, True, True, True, True
        for arg in args:
            if args[arg] is not None:
                if arg == "classifier":
                    classifier = Classification.classifier_name == args[arg]
                if arg == "class":
                    class_ = Classification.class_name == args[arg]
                if arg == "ndet_min":
                    ndet_min = AstroObject.nobs >= args[arg]
                if arg == "mjd":
                    mjd = AstroObject.firstmjd >= args[arg]
                if arg == "probability":
                    probability = Classification.probability >= args[arg]
        return classifier, class_, ndet_min, mjd, probability


@api.route("/<id>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Object not found")
class Object(Resource):
    @api.doc("get_object")
    @api.marshal_with(object_model)
    def get(self, id):
        """Fetch an object given its identifier"""
        result = (
            db.session.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        )
        if result:
            return result
        else:
            raise NotFound("Object not found")
