from flask_restful import fields, marshal_with, reqparse, Resource
from flask_restful_swagger_3 import Schema, swagger
from flask import jsonify

from db_plugins.db.sql import query
from db_plugins.db.sql.models import FeaturesObject
from db_plugins.db.sql.serializers import FeaturesSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class FeaturesModel(Schema):
    type = 'object'
    resource_fields = {
        "version": fields.String
    }


class FeaturesResponseModel(Schema):
    type = 'array'
    items = FeaturesModel


class FeaturesResource(Resource):
    def get(self, object_id, features_version):
        result = query(session, FeaturesObject, None, None, None,
                       FeaturesObject.object_id == object_id,
                       FeaturesObject.features_version == features_version)
        serializer = FeaturesSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class FeaturesListResource(Resource):
    def get(self):
        result = query(session, FeaturesObject, 1, 1)
        serializer = FeaturesSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)