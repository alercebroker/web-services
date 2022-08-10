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
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_lightcurve"])
    @decorators.check_permissions_decorator
    @api.doc("lightcurve")
    @api.marshal_with(models.light_curve, skip_none=True)
    @api.expect(parsers.filters)
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
        """
        Gets detections and non detections
        """
        args = {"aid": id, **parsers.filters.parse_args()}
        command = command_factory(
            payload=LightCurvePayload(args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectDetections(Resource):
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_detections"])
    @decorators.check_permissions_decorator
    @api.doc("detections")
    @api.marshal_list_with(models.detection, skip_none=True)
    @api.expect(parsers.filters, parsers.pagination, parsers.order)
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
        """
        Just the detections
        """
        args = {"aid": id, **parsers.filters.parse_args()}
        paginate_args = parsers.pagination.parse_args()
        sort_args = parsers.order.parse_args()
        command = command_factory(
            payload=LightCurvePayload(args, paginate_args, sort_args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/non_detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class NonDetections(Resource):
    @decorators.set_permissions_decorator(["admin", "basic_user"])
    @decorators.set_filters_decorator(["filter_atlas_non_detections"])
    @decorators.check_permissions_decorator
    @api.doc("non_detections")
    @api.marshal_list_with(models.non_detection, skip_none=True)
    @api.expect(parsers.filters, parsers.pagination, parsers.order)
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
        """
        Just non detections
        """
        args = {"aid": id, **parsers.filters.parse_args()}
        paginate_args = parsers.pagination.parse_args()
        sort_args = parsers.order.parse_args()
        command = command_factory(
            payload=LightCurvePayload(args, paginate_args, sort_args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
