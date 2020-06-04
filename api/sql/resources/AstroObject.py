from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from db_plugins.db.sql.serializers import AstroObjectSchema, ClassificationSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


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
        result = query(session, AstroObject, 1, 10, None)
        astro_objects = result["results"]
        res = []

        for astro_object in astro_objects:

            oid = astro_object.oid

            #result_classifications = query(session, Classification, 1, 1, None, Classification.astro_object == oid)
            #classification = result_classifications["results"]

            #result_xmatch = query(session, Xmatch, 1, 1, None, Xmatch.catalog_oid == oid)
            #xmatch = result_xmatch["results"]
            #if type(xmatch) == list:
            #    print(xmatch)
            #    xmatch = xmatch[0]

            data = {
                "oid": astro_object.oid,
                "num_detections": astro_object.nobs,
                "firstmjd": astro_object.firstmjd,
                "lastmjf": astro_object.lastmjd,
                "ra": astro_object.meanra,
                "dec": astro_object.meandec,
                #"xmatch_class_catalog": xmatch.catalog_id,
                #"class": classification.class_name,
                #"probability": classification.probability,
            }

            res.append(data)

        return res


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