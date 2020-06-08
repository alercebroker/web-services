from flask_restful import fields, marshal_with, reqparse, Resource
from flask_restful_swagger_3 import Schema, swagger
from flask import jsonify
from api.sql.resources.Class import ClassSchema
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Classification
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class ClassificationModel(Schema):
    type = 'object'
    resource_fields = {
        "name": fields.String,
        "classifier_name": fields.String,
        "class_name": fields.String,
        "probability": fields.Float,
        "probabilities": fields.List(fields.Float)
    }


class ClassificationResponseModel(Schema):
    type = 'array'
    items = ClassSchema


class ClassificationModel(Schema):
    type = 'object'
    resource_fields = {
        "oid": fields.String,
        "classifier": fields.Integer,
        "class_name": fields.String,
        "probability": fields.Integer,
        "probabilities": fields.List(fields.Integer),
    }


class ClassificationResource(Resource):
    """
    Class individual resource
    """
    @swagger.doc({
        "summary": "Gets an individual class",
        "description": "long description",
        "parameters": [
            {
                "name": "astro_object",
                "in": "path",
                "description": "Id of the astro object",
                "required": True,
                "schema":{
                    "type": "string"
                }
            },
            {
                "name": "classifier_name",
                "in": "path",
                "description": "Name of the classifier",
                "required": True,
                "schema": {
                    "type": "string"
                }
            }
        ],
        "responses": {
            '200': {
                'description': 'Class got',
                'content': {
                    "application/json": {
                        'schema': ClassificationModel
                    }
                }
            }
        }
    }
    )
    def get(self, astro_object, classifier_name):
        result = query(session, Classification, None, None, None,
                       Classification.astro_object == astro_object,
                       Classification.classifier_name == classifier_name)
        serializer = ClassificationSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ClassificationListResource(Resource):
    """
    Class list resource
    """
    @swagger.doc({
        "summary": "Gets a list of classifications",
        "description": "long description",
        "responses": {
            '200': {
                'description': 'Classifications got',
                'content': {
                    "application/json": {
                        'schema': ClassificationResponseModel
                    }
                }
            }
        }
    }
    )
    def get(self):
        result = query(session, Classification, 1, 1)
        serializer = ClassificationSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)