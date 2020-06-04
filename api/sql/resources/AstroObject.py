from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument('oid')
parser.add_argument('classifier')
parser.add_argument('class')
parser.add_argument('ndet')

class ObjectModel(Schema):
    type = 'object'
    resource_fields = {
        "oid": fields.String,
        "ndet": fields.Integer,
        "firstmjd": fields.Float,
        "lastmjd": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "xmatch_class_catalog": fields.String,
        "class_name": fields.Float,
        "probability": fields.Float
    }
class ResponseModel(Schema):
    type = 'object'
    resource_fields = {
        "total": fields.Integer,
        "results": fields.List(fields.Nested(ObjectModel.resource_fields))
    }


class ObjectResource(Resource):
    """
    Astro objects individual resource
    """
    @swagger.doc({
        "summary": "Gets an individual object",
        "description": "long description",
        "parameters": [
            {
                "name": "oid",
                "in": "path",
                "description": "Identifier for the object",
                "required": True,
                "schema": {
                    "type": "string"
                }
            }
        ],
        "responses": {
            '200': {
                'description': 'Ok',
                'content': {
                    'application/json': {
                        'schema': ObjectModel
                    }
                }
            }
        }
    }
    )
    def get(self, oid):
        result = query(session, AstroObject, None, None,
                       None, AstroObject.oid == oid)
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ObjectListResource(Resource):
    """
    Astro object list resource
    """
    @swagger.doc({
        "summary": "Gets a list of objects",
        "description": "long description",
        "responses": {
            '200': {
                'description': 'Ok',
                'content': {
                    'application/json': {
                        'schema': ResponseModel
                    }
                }
            }
        }
    }
    )
    @marshal_with(ResponseModel.resource_fields)
    def get(self):
        args = parser.parse_args()
        objects = query(session, AstroObject, 1, 10, None,)
        return objects





class ObjectClassificationsResource(Resource):

    def get(self, oid):
        result = query(session, AstroObject, None, None,
                       None, AstroObject.oid == oid)
        classifications = query(
            session, Classification, None, None, None, Classification.astro_object == oid)

        serializer = AstroObjectSchema()
        classification_serializer = ClassificationSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_classification = classifications["results"][0]
        res_classification = classification_serializer.dump(obj_classification)
        # TODO: como juntar estos datos
        return jsonify(res)


class ObjectXmatchResource(Resource):

    def get(self, oid):
        result = query(session, AstroObject, None, None,
                       None, AstroObject.oid == oid)
        xmatch = query(session, Xmatch, None, None,
                       None, Xmatch.astro_object == oid)

        serializer = AstroObjectSchema()
        xmatch_serializer = XmatchSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_xmatch = xmatch["results"][0]
        res_xmatch = xmatch_serializer.dump(obj_xmatch)
        # TODO: como juntar estos datos
        return jsonify(res)
