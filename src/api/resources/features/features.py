from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from flask_restx import Namespace, Resource

from api.container import AppContainer
from core.features.domain import FeaturesPayload
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from . import models, parsers

api = Namespace("features", description="Features related operations")
api.models[models.feature.name] = models.feature


@api.route("/<id>/features")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Features(Resource):
    @api.doc("features")
    @api.expect(parsers.filters)
    @api.marshal_list_with(models.feature)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.features_package.get_features.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """
        Gets list of all features.
        """
        args = parsers.filters.parse_args()
        command = command_factory(
            payload=FeaturesPayload(id, **args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/features/<name>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Feature(Resource):
    @api.doc("features")
    @api.expect(parsers.filters)
    @api.marshal_with(models.feature)
    @inject
    def get(
        self,
        id,
        name,
        command_factory: Factory[Command] = Provide[
            AppContainer.features_package.get_features.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """
        Gets a single Feature
        """
        args = parsers.filters.parse_args()
        command = command_factory(
            payload=FeaturesPayload(id, name=name, **args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
