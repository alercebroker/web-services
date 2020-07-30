from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql import models
from .models import probability_model
from .parsers import prob_parser
from werkzeug.exceptions import NotFound
from ...db import db

api = Namespace("probabilities", description="Class probabilities related operations")
api.models[probability_model.name] = probability_model


@api.route("/<id>/probabilities")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Probabilities(Resource):
    @api.doc("probabilities")
    @api.expect(prob_parser)
    @api.marshal_list_with(probability_model)
    def get(self, id):
        obj = db.query(models.Object).find_one(filter_by={"oid": id})
        if obj:
            args = prob_parser.parse_args()
            probs = db.query(models.Probability).filter(models.Probability.oid == obj.oid) #obj.probabilities
            if args["classifier"]:
                probs = probs.filter(models.Probability.classifier_name == args["classifier"] )
            if args["classifier_version"]:
                probs = probs.filter(models.Probability.classifier_version == args["classifier_version"] )
            return probs.all()
        else:
            raise NotFound("Object not found")
