from flask_restx import Namespace, Resource
from flask_restx import reqparse
from .models import (
    feature_model
)
from .parsers import fid_parser
from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from ...db import db

api = Namespace("features", description="Features related operations")
api.models[feature_model.name] = feature_model

@api.route("/features/<id>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Features(Resource):
    @api.doc("features")
    @api.expect(fid_parser)
    @api.marshal_list_with(feature_model)
    def get(self, id):
        """
        Gets list of all features.
        """
        args = fid_parser.parse_args()
        obj = db.query(models.Object).filter(models.Object.oid == id).one_or_none()
        if obj:
            q = db.query(models.Feature).filter(models.Feature.oid == obj.oid)
            if args.fid is not None:
                q = q.filter(models.Feature.fid == args.fid)
            if args.version is not None:
                q = q.filter(models.Feature.version == args.version)
            return q.all()
        else:
            raise NotFound("Object not found")

@api.route("/features/<id>/<name>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Feature(Resource):
    @api.doc("features")
    @api.expect(fid_parser)
    @api.marshal_with(feature_model)
    def get(self, id, name):
        """
        Gets a single Feature
        """
        args = fid_parser.parse_args()
        obj = db.query(models.Object,models.Object.oid).filter(models.Object.oid == id).one_or_none()
        if obj:
            q = db.query(models.Feature).filter(models.Feature.name == name).filter(models.Feature.oid == obj.oid)
            if args.fid is not None:
                q = q.filter(models.Feature.fid == args.fid)
            if args.version is not None:
                q = q.filter(models.Feature.version == args.version)
            return q.all()
        else:
            raise NotFound("Object not found")
