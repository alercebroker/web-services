from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from flask_restx import Namespace, Resource

from api.container import AppContainer
from core.probabilities.domain import ProbabilitiesPayload
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from . import models, parsers


api = Namespace(
    "probabilities", description="Class probabilities related operations"
)
api.models[models.probability.name] = models.probability


@api.route("/<id>/probabilities")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Probabilities(Resource):
    @api.doc("probabilities")
    @api.marshal_list_with(models.probability)
    @api.expect(parsers.filters)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.probabilities_package.get_probabilities.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        args = parsers.filters.parse_args()
        command = command_factory(
            payload=ProbabilitiesPayload(id, **args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
