from flask_restx import Namespace, Resource
from db_plugins.db.sql import models
from .models import probability_model
from .parsers import prob_parser
from werkzeug.exceptions import NotFound
from ...db import db
from typing import List

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
            probs = db.query(models.Probability).filter(
                models.Probability.oid == obj.oid
            )  # obj.probabilities
            if args["classifier"]:
                probs = probs.filter(
                    models.Probability.classifier_name == args["classifier"]
                )
            if args["classifier_version"]:
                probs = probs.filter(
                    models.Probability.classifier_version == args["classifier_version"]
                )

            taxonomy = db.query(models.Taxonomy).all()
            return self.order_probs(probs.all(), taxonomy)
        else:
            raise NotFound

    def order_probs(self, probs: List, taxonomy: List):
        def sorting_order(e):
            order = None
            for tax in taxonomy:
                if tax.classifier_name == e.classifier_name:
                    latest = tax
            order = dict(zip(latest.classes, range(len(latest.classes))))
            return order[e.class_name]

        probs.sort(key=sorting_order)
        return probs
