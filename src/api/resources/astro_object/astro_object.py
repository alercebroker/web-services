from dependency_injector.providers import Factory
from dependency_injector.wiring import inject, Provide
from flask_restx import Namespace, Resource

from api.container import AppContainer
from core.astro_object.domain import (
    ListAstroObjectPayload,
    SingleAstroObjectPayload,
    LimitsAstroObjectPayload,
)
from shared.interface.command import Command, ResultHandler

from . import models, parsers


api = Namespace("objects", description="Objects related operations")
api.models[models.object_list.name] = models.object_list
api.models[models.object_item.name] = models.object_item
api.models[models.single_object.name] = models.single_object
api.models[models.limit_values.name] = models.limit_values
api.models[models.xmatch.name] = models.xmatch


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectList(Resource):
    @api.doc("list_object")
    @api.expect(parsers.filters, parsers.pagination, parsers.order)
    @api.marshal_with(models.object_list)
    @inject
    def get(
        self,
        command_factory: Factory[Command] = Provide[
            AppContainer.astro_object_package.get_list_object.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """List all objects by given filters"""
        command = command_factory(
            payload=ListAstroObjectPayload(
                parsers.filters.parse_args(),
                paginate_args=parsers.pagination.parse_args(),
                sort_args=parsers.order.parse_args(),
            ),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Object not found")
class Object(Resource):
    @api.doc("get_object")
    @api.marshal_with(models.single_object)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.astro_object_package.get_single_object.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """Fetch an object given its identifier"""
        command = command_factory(
            payload=SingleAstroObjectPayload(id), handler=result_handler
        )
        command.execute()
        return result_handler.result


@api.route("/limit_values")
@api.response(200, "Success")
class LimitValues(Resource):
    @api.doc("limit_values")
    @api.marshal_with(models.limit_values)
    @inject
    def get(
        self,
        command_factory: Factory[Command] = Provide[
            AppContainer.astro_object_package.get_limits.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """Gets min and max values for objects number of detections and detection dates"""
        command = command_factory(
            payload=LimitsAstroObjectPayload(), handler=result_handler
        )
        command.execute()
        return result_handler.result
