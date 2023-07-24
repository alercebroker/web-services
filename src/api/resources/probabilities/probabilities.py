from flask_restx import Namespace, Resource
from db_plugins.db.sql import models
from .models import probability_model
from .parsers import prob_parser
from werkzeug.exceptions import NotFound
from dependency_injector.wiring import inject, Provide
from api.container import AppContainer
from typing import List

api = Namespace(
    "probabilities", description="Class probabilities related operations"
)
api.models[probability_model.name] = probability_model


@api.route("/<id>/probabilities")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Probabilities(Resource):
    @api.doc("probabilities")
    @api.expect(prob_parser)
    @api.marshal_list_with(probability_model)
    @inject
    def get(
        self,
        id,
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        args = prob_parser.parse_args()
        with session_factory() as session:
            obj = session.query(models.Object).filter_by(oid=id).one_or_none()
            if obj:
                probs = session.query(models.Probability).filter(
                    models.Probability.oid == obj.oid
                )  # obj.probabilities
                if args["classifier"]:
                    probs = probs.filter(
                        models.Probability.classifier_name
                        == args["classifier"]
                    )
                if args["classifier_version"]:
                    probs = probs.filter(
                        models.Probability.classifier_version
                        == args["classifier_version"]
                    )

                taxonomy = session.query(models.Taxonomy).all()
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
