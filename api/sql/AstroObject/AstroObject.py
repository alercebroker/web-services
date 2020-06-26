from flask_restx import Namespace, Resource
from db_plugins.db.sql import models
from ...sql.AstroObject.models import object_list_item, object_list, object_item
from ...sql.AstroObject.parsers import parser
from sqlalchemy import text
from astropy import units
import argparse
from werkzeug.exceptions import NotFound
from ...db import db

api = Namespace("objects", description="Objects related operations")
api.models[object_list_item.name] = object_list_item
api.models[object_list.name] = object_list
api.models[object_item.name] = object_item


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectList(Resource):
    @api.doc("list_object")
    @api.expect(parser)
    @api.marshal_with(object_list)
    def get(self):
        """List all objects by given filters"""
        args = parser.parse_args()
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
            db.query(models.AstroObject, models.Classification)
            .outerjoin(models.AstroObject.classifications)
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
                    classifier = models.Classification.classifier_name == args[arg]
                if arg == "class":
                    class_ = models.Classification.class_name == args[arg]
                if arg == "ndet":
                    ndet = models.AstroObject.nobs >= args[arg][0]
                    if len(args[arg]) > 1:
                        ndet = ndet & (models.AstroObject.nobs <= args[arg][1])
                if arg == "firstmjd":
                    firstmjd = models.AstroObject.firstmjd >= args[arg][0]
                    if len(args[arg]) > 1:
                        firstmjd = firstmjd & (
                            models.AstroObject.firstmjd <= args[arg][1]
                        )
                if arg == "lastmjd":
                    lastmjd = models.AstroObject.lastmjd >= args[arg][0]
                    if len(args[arg]) > 1:
                        lastmjd = lastmjd & (models.AstroObject.lastmjd <= args[arg][1])
                if arg == "probability":
                    probability = models.Classification.probability >= args[arg]
        conesearch = self._create_conesearch_statement(args)
        return classifier, class_, ndet, firstmjd, lastmjd, probability, conesearch

    def _create_conesearch_statement(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args["radius"]
        except KeyError:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
        else:
            return True

    def _parse_conesearch_args(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args["radius"]
        except KeyError:
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
            db.query(models.AstroObject)
            .filter(models.AstroObject.oid == id)
            .one_or_none()
        )
        if result:
            return result
        else:
            raise NotFound("Object not found")
