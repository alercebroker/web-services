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
api.models[models.light_curve_model.name] = models.light_curve_model
api.models[models.detection_model.name] = models.detection_model
api.models[models.non_detection_model.name] = models.non_detection_model


@api.route("/<id>/lightcurve")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class LightCurve(Resource):
    @api.doc("lightcurve")
    @api.expect(parsers.survey_id_parser)
    @api.marshal_with(models.light_curve_model, skip_none=True)
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
        """
        Gets detections and non detections
        """
        args = parsers.survey_id_parser.parse_args()
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
    @api.marshal_list_with(models.detection_model, skip_none=True)
    @api.expect(parsers.survey_id_parser)
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
        """
        Just the detections
        """
        args = parsers.survey_id_parser.parse_args()
        command = command_factory(
            payload=LightCurvePayload(id, args),
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
    @api.marshal_list_with(models.non_detection_model, skip_none=True)
    @api.expect(parsers.survey_id_parser)
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
        """
        Just non detections
        """
        args = parsers.survey_id_parser.parse_args()
        command = command_factory(
            payload=LightCurvePayload(id, args),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
