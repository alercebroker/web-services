from flask_restx import Namespace, Resource
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import (
    object_list_item,
    object_list,
    object_item,
    limit_values_model,
)
from .parsers import create_parsers

from dependency_injector.providers import Factory
from api.container import AppContainer
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from core.astro_object.payload import AstroObjectPayload
from dependency_injector.wiring import inject, Provide

api = Namespace("objects", description="Objects related operations")
api.models[object_list_item.name] = object_list_item
api.models[object_list.name] = object_list
api.models[object_item.name] = object_item
api.models[limit_values_model.name] = limit_values_model

limiter = Limiter(key_func=get_remote_address, default_limits=["30/second"])

(
    filter_parser,
    order_parser,
    pagination_parser,
) = create_parsers()


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectList(Resource):
    decorators = [limiter.limit("30/sec")]

    @api.doc("list_object")
    @api.expect(filter_parser, pagination_parser, order_parser)
    @api.marshal_with(object_list)
    @inject
    def get(
        self,
        command_factory: Factory[Command] = Provide[
            AppContainer.astro_object_package.get_object_list.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """List all objects by given filters"""
        command = command_factory(
            payload=AstroObjectPayload(
                filter_parser.parse_args(),
                paginate_args=pagination_parser.parse_args(),
                sort_args=order_parser.parse_args(),
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
    @api.marshal_with(object_item)
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
            payload=AstroObjectPayload({"oid": id}), handler=result_handler
        )
        command.execute()
        return result_handler.result


@api.route("/limit_values")
@api.response(200, "Success")
class LimitValues(Resource):
    @api.doc("limit_values")
    @api.marshal_with(limit_values_model)
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
            payload=AstroObjectPayload({}), handler=result_handler
        )
        command.execute()
        return result_handler.result
