from flask_restful import fields, marshal_with, reqparse, Resource
from flask_restful_swagger_3 import Schema, swagger
from flask import jsonify

from db_plugins.db.sql import query
from db_plugins.db.sql.models import Classifier
from db_plugins.db.sql.serializers import ClassifierSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class ClassifierModel(Schema):
    type = 'object'
    resource_fields = {
        "name": fields.String,
        "taxonomy_name": fields.String
    }


class ClassifierResponseModel(Schema):
    type = 'array'
    items = ClassifierModel


class ClassifierResource(Resource):
    def get(self, name):
        result = query(session, Classifier, None, None, None, Classifier.name == name)
        serializer = ClassifierSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ClassifierListResource(Resource):
    def get(self):
        result = query(session, Classifier, 1, 1)
        serializer = ClassifierSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)