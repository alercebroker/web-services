from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import NonDetection
from db_plugins.db.sql.serializers import NonDetectionSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class DetectionModel(Schema):
    type = 'object'
    resource_fields = {
        "name": fields.String,
        "acronym": fields.String
    }


class DetectionResponseModel(Schema):
    type = 'array'
    items = DetectionModel


class NonDetectionResource(Resource):
    def get(self, oid, fid, datetime):
        result = query(session, NonDetection, None, None, None,
                       NonDetection.oid == oid,
                       NonDetection.fid == fid,
                       NonDetection.datetime == datetime)
        serializer = NonDetectionSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class NonDetectionListResource(Resource):
    def get(self):
        result = query(session, NonDetection, 1, 1)
        serializer = NonDetectionSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)