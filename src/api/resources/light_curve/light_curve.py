from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from flask_restx import Namespace, Resource
from ralidator_flask import decorators

from api.container import AppContainer
from core.light_curve.domain import LightCurvePayload
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from . import models, parsers


api = Namespace("lightcurve", description="LightCurve related operations")
api.models[models.light_curve.name] = models.light_curve
api.models[models.detection.name] = models.detection
api.models[models.non_detection.name] = models.non_detection


@api.route("/<id>/lightcurve")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class LightCurve(Resource):
    @api.doc("lightcurve")
    @api.expect(parsers.filters)
    @api.marshal_with(models.light_curve, skip_none=True)
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_lightcurve"])
    @decorators.check_permissions_decorator
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_lightcurve.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """Gets detections and non detections"""
        args = parsers.filters.parse_args()
        command = command_factory(
            payload=LightCurvePayload(id, args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectDetections(Resource):
    @api.doc("detections")
    @api.expect(parsers.filters, parsers.pagination, parsers.order)
    @api.marshal_list_with(models.detection, skip_none=True)
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_detections"])
    @decorators.check_permissions_decorator
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_detections.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """Gets list of all detections"""
        args = parsers.filters.parse_args()
        paginate_args = parsers.pagination.parse_args()
        sort_args = parsers.order.parse_args()
        command = command_factory(
            payload=LightCurvePayload(id, args, paginate_args, sort_args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/non_detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class NonDetections(Resource):
    @api.doc("non_detections")
    @api.expect(parsers.filters, parsers.pagination, parsers.order)
    @api.marshal_list_with(models.non_detection, skip_none=True)
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_non_detections"])
    @decorators.check_permissions_decorator
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_non_detections.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """Gets list of all non-detections"""
        args = parsers.filters.parse_args()
        paginate_args = parsers.pagination.parse_args()
        sort_args = parsers.order.parse_args()
        command = command_factory(
            payload=LightCurvePayload(id, args, paginate_args, sort_args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
