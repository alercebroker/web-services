from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from flask_restx import Namespace, Resource

from api.container import AppContainer
from core.magstats.domain import MagStatsPayload
from shared.interface.command import Command, ResultHandler
from . import models

api = Namespace(
    "magnitude statistics",
    description="Magnitude Statistics related operations",
)
api.models[models.magstats.name] = models.magstats


@api.route("/<id>/magstats")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class MagStats(Resource):
    @api.doc("magstats")
    @api.marshal_list_with(models.magstats, skip_none=True)
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
        command = command_factory(
            payload=MagStatsPayload(id),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
