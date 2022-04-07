from flask import make_response
from flask_restx import Namespace, Resource
from .parsers import survey_id_parser
from .models import (
    light_curve_model,
    detection_model,
    non_detection_model,
)
from ...database_access.commands import (
    GetLightCurve,
    GetDetections,
    GetNonDetections,
)
from ...result_handlers.view_result_handlers import ViewResultHandler

api = Namespace("lightcurve", description="LightCurve related operations")
api.models[light_curve_model.name] = light_curve_model
api.models[detection_model.name] = detection_model
api.models[non_detection_model.name] = non_detection_model


@api.route("/<id>/lightcurve")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class LightCurve(Resource):
    @api.doc("lightcurve")
    @api.marshal_with(light_curve_model, skip_none=True)
    @api.expect(survey_id_parser)
    def get(self, id):
        """
        Gets detections and non detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]

        response = make_response()
        result_handler = ViewResultHandler(response)

        get_lightcurve_command = GetLightCurve(id, survey_id, result_handler)
        get_lightcurve_command.execute()

        return result_handler.get_result()

@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectDetections(Resource):
    @api.doc("detections")
    @api.marshal_list_with(detection_model, skip_none=True)
    @api.expect(survey_id_parser)
    def get(self, id):
        """
        Just the detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]

        response = make_response()
        result_handler = ViewResultHandler(response)

        get_lightcurve_command = GetDetections(id, survey_id, result_handler)
        get_lightcurve_command.execute()
        
        return result_handler.get_result()

@api.route("/<id>/non_detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class NonDetections(Resource):
    @api.doc("non_detections")
    @api.marshal_list_with(non_detection_model, skip_none=True)
    @api.expect(survey_id_parser)
    def get(self, id):
        """
        Just non detections
        """
        survey_id = survey_id_parser.parse_args()["survey_id"]

        result_handler = ViewResultHandler()

        get_lightcurve_command = GetNonDetections(id, survey_id, result_handler)
        get_lightcurve_command.execute()
        
        return result_handler.get_result()
