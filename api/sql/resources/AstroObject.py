from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from db_plugins.db.sql.serializers import AstroObjectSchema, ClassificationSchema, XmatchSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class ObjectModel(Schema):
    type = 'object'
    resource_fields = {
        "oid": fields.String,
        "num_detections": fields.Integer,
        "first_date": fields.Float,
        "last_date": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "xmatch_class_catalog": fields.String,
        "class": fields.Float,
        "probability": fields.Float,
    }


class ObjectResource(Resource):
    """
    Astro objects individual resource
    """
    @swagger.doc({
        "summary": "Gets an individual object",
        "description":"long description",
        "parameters":[
            {
                "name": "oid",
                "in": "path",
                "description": "Identifier for the object",
                "required": True,
                "schema":{
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
    def get(self,oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        serializer = AstroObjectSchema()
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
                        'schema': ObjectModel
                    }
                }
            }
        }
    }
    )
    @marshal_with(ObjectModel.resource_fields)
    def get(self):
        result = query(session, AstroObject, None, None, None, True)
        serializer = AstroObjectSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)


class ObjectQueryListResource(Resource):
    """
    Astro object list resource joining with Xmatch and Classifications
    """
    @swagger.doc({
        "summary": "Gets a list of objects base on a query",
        "description": "long description",
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
    @marshal_with(ObjectModel.resource_fields)
    def get(self):
        result = query(session, AstroObject, None, None, None)
        serializer = AstroObjectSchema()
        obj_astro = result["results"][0]
        res_astro = serializer.dump(obj_astro)

        classifications = query(session, Classification, None, None, None)
        classification_serializer = ClassificationSchema()
        obj_classification = classifications["results"][0]
        res_classification = classification_serializer.dump(obj_classification)

        xmatch = query(session, Xmatch, None, None, None)
        xmatch_serializer = XmatchSchema()
        obj_xmatch = xmatch["results"][0]
        res_xmatch = xmatch_serializer.dump(obj_xmatch)

        res = {
            "oid": 2,
            "num_detections": None,
            "first_date": None,
            "last_date": None,
            "ra": None,
            "dec": None,
            "xmatch_class_catalog": None,
            "class": None,
            "probability": None,
        }

        return jsonify(res)


class ObjectClassificationsResource(Resource):

    @marshal_with(ObjectModel.resource_fields)
    def get(self, oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        classifications = query(session, Classification, None, None, None, Classification.astro_object == oid)

        serializer = AstroObjectSchema()
        classification_serializer = ClassificationSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_classification = classifications["results"][0]
        res_classification = classification_serializer.dump(obj_classification)
        #TODO: como juntar estos datos
        return jsonify(res)


class ObjectXmatchResource(Resource):

    @marshal_with(ObjectModel.resource_fields)
    def get(self, oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        xmatch = query(session, Xmatch, None, None, None, Xmatch.astro_object == oid)

        serializer = AstroObjectSchema()
        xmatch_serializer = XmatchSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_xmatch = xmatch["results"][0]
        res_xmatch = xmatch_serializer.dump(obj_xmatch)
        #TODO: como juntar estos datos
        return jsonify(res)