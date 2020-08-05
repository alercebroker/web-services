from flask_restx import Namespace, Resource
from flask_restx import reqparse
from .models import (
    light_curve_model,
    detection_model,
    non_detection_model,
)
from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from ...db import db


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
    @api.marshal_with(light_curve_model)
    def get(self, id):
        """
        Gets detections and non detections
        """
        obj = (
            db.query(models.Object)
            .filter(models.Object.oid == id)
            .one_or_none()
        )
        if obj:
            light_curve = obj.get_lightcurve()
            for det in light_curve["detections"]:
                det.phase = 0  # (det.mjd % obj.period) / obj.period
            return light_curve
        else:
            return {}


@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectDetections(Resource):
    @api.doc("detections")
    @api.marshal_list_with(detection_model)
    def get(self, id):
        """
        Just the detections
        """
        result = (
            db.query(models.Object)
            .filter(models.Object.oid == id)
            .one_or_none()
        )
        if result:
            return result.detections
        else:
            return []


@api.route("/<id>/non_detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class NonDetections(Resource):
    @api.doc("non_detections")
    @api.marshal_list_with(non_detection_model)
    def get(self, id):
        """
        Just non detections
        """
        result = (
            db.query(models.Object)
            .filter(models.Object.oid == id)
            .one_or_none()
        )
        if result:
            return result.non_detections
        else:
            return []

