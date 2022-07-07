from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from flask_restx import Namespace, Resource

from .models import magstats_model
from .parsers import survey_id_parser
from api.container import AppContainer
from core.magstats.domain.magstats_service import MagStatsServicePayload
from shared.interface.command import Command, ResultHandler

api = Namespace(
    "magnitude statistics",
    description="Magnitude Statistics related operations",
)
api.models[magstats_model.name] = magstats_model


@api.route("/<id>/magstats")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class MagStats(Resource):
    @api.doc("magstats")
    @api.marshal_list_with(magstats_model, skip_none=True)
    @api.expect(survey_id_parser)
    @inject
    def get(
            self,
            id,
            command_factory: Factory[Command] = Provide[
                AppContainer.magstats_package.command.provider
            ],
            result_handler: ResultHandler = Provide[
                AppContainer.view_result_handler]
    ):
        survey_id = survey_id_parser.parse_args()["survey_id"]
        command = command_factory(
            payload=MagStatsServicePayload(id, survey_id),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
