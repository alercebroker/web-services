from flask_restful import fields, marshal_with, reqparse, Resource
from flask_restful_swagger_2 import Schema
from flask_restful_swagger_3 import swagger
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Classification
from db_plugins.db.sql.serializers import ClassificationSchema

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}


class ObjectModel(Schema):
    type = 'object'
    resource_fields = {
        'oid': fields.Integer
    }


class ClassificationResource(Resource):
    def get(self, astro_object, classifier_name):
        result = query(session, Classification, None, None, None,
                       Classification.astro_object == astro_object,
                       Classification.classifier_name == classifier_name)
        serializer = ClassificationSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ClassificationListResource(Resource):
    def get(self):
        result = query(session, Classification, 1, 1)
        serializer = ClassificationSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)