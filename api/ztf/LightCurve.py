from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from werkzeug.exceptions import NotFound
from ..db import db

api = Namespace("lightcurve", description="LightCurve related operations")

detection_model = api.model(
    "Detection",
    {
        "mjd": fields.Float,
        "candid": fields.String,
        "fid": fields.Integer,
        "pid": fields.Integer,
        "diffmaglim": fields.Float,
        "isdiffpos": fields.Integer,
        "nid": fields.Integer,
        "distnr": fields.Float,
        "magpsf": fields.Float,
        "magpsf_corr": fields.Float,
        "magap": fields.Float,
        "magap_corr": fields.Float,
        "sigmapsf": fields.Float,
        "sigmapsf_corr": fields.Float,
        "sigmagap": fields.Float,
        "sigmagap_corr": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "rb": fields.Float,
        "rbversion": fields.String,
        "drb": fields.Float,
        "magapbig": fields.Float,
        "sigmagapbig": fields.Float,
        "rfid": fields.Integer,
        "has_stamp": fields.Boolean,
        "corrected": fields.Boolean,
        "dubious": fields.Boolean,
        "candid_alert": fields.String,
        "step_id_corr": fields.String,
    },
)

non_detection_model = api.model(
    "Non Detection",
    {"mjd": fields.Float, "fid": fields.Integer, "diffmaglim": fields.Float},
)

light_curve_model = api.model(
    "Light Curve",
    {
        "detections": fields.List(fields.Nested(detection_model)),
        "non_detections": fields.List(fields.Nested(non_detection_model)),
    },
)


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
        result = db.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        return result.get_lightcurve()


@api.route("/<id>/detections")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Detections(Resource):
    @api.doc("detections")
    @api.marshal_list_with(detection_model)
    def get(self, id):
        """
        Just the detections
        """
        result = db.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        return result.detections


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
        result = db.query(AstroObject).filter(AstroObject.oid == id).one_or_none()
        return result.non_detections
