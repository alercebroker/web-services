from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql import models
from .models import probability_model
from .parsers import prob_parser
from werkzeug.exceptions import NotFound
from ...db import db
from typing import List

api = Namespace("probabilities", description="Class probabilities related operations")
api.models[probability_model.name] = probability_model

LC_CLASSIFIER_ORDER = {
    "SNIa": 0,
    "SNIbc": 1,
    "SNII": 2,
    "SLSN": 3,
    "QSO": 4,
    "AGN": 5,
    "Blazar": 6,
    "YSO": 7,
    "CV/Nova": 8,
    "LPV": 9,
    "E": 10,
    "DSCT": 11,
    "RRL": 12,
    "CEP": 13,
    "Periodic-Other": 14,
    "Periodic": 15,
    "Transient": 16,
    "Stochastic": 17,
}

STAMP_CLASSIFIER_ORDER = {"AGN": 0, "SN": 1, "VS": 2, "asteroid": 3, "bogus": 4}


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
            return self.order_probs(probs.all())
        else:
            raise NotFound

    def order_probs(self, probs: List):
        def sorting_order(e):
            if "lc_classifier" in e["classifier_name"]:
                return LC_CLASSIFIER_ORDER[e["class_name"]]
            elif "stamp_classifier" in e["classifier_name"]:
                return STAMP_CLASSIFIER_ORDER[e["class_name"]]

        probs.sort(key=sorting_order)
        return probs
