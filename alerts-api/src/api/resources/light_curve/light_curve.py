from flask_restx import Namespace, Resource
from .parsers import survey_id_parser
from .models import (
    light_curve_model,
    detection_model,
    non_detection_model,
)
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from api.container import AppContainer
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from core.light_curve.domain.lightcurve_service import LightcurveServicePayload
from ralidator_flask.decorators import (
    set_permissions_decorator,
    set_filters_decorator,
    check_permissions_decorator,
)

api = Namespace("lightcurve", description="LightCurve related operations")
api.models[light_curve_model.name] = light_curve_model
api.models[detection_model.name] = detection_model
api.models[non_detection_model.name] = non_detection_model


@api.route("/<id>/lightcurve")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class LightCurve(Resource):
    @set_permissions_decorator(["admin", "basic_user"])
    @set_filters_decorator(["filter_atlas_lightcurve"])
    @check_permissions_decorator
    @api.doc("lightcurve")
    @api.marshal_with(light_curve_model, skip_none=True)
    @api.expect(survey_id_parser)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_lightcurve_command.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """
        Gets detections and non detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]
        command = command_factory(
            payload=LightcurveServicePayload(id, survey_id),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectDetections(Resource):
    @set_permissions_decorator(["admin", "basic_user"])
    @set_filters_decorator(["filter_atlas_detections"])
    @check_permissions_decorator
    @api.doc("detections")
    @api.marshal_list_with(detection_model, skip_none=True)
    @api.expect(survey_id_parser)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_detections_command.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """
        Just the detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]
        command = command_factory(
            payload=LightcurveServicePayload(id, survey_id),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<id>/non_detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class NonDetections(Resource):
    @set_permissions_decorator(["admin", "basic_user"])
    @set_filters_decorator(["filter_atlas_non_detections"])
    @check_permissions_decorator
    @api.doc("non_detections")
    @api.marshal_list_with(non_detection_model, skip_none=True)
    @api.expect(survey_id_parser)
    @inject
    def get(
        self,
        id,
        command_factory: Factory[Command] = Provide[
            AppContainer.lightcurve_package.get_non_detections_command.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        """
        Just non detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]
        command = command_factory(
            payload=LightcurveServicePayload(id, survey_id),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
