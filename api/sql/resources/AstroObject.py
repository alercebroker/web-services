from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful_swagger_3 import swagger
from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject
from db_plugins.db.sql.serializers import AstroObjectSchema
from .. import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}


class ObjectResource(Resource):
    """
    Astro objects individual resource
    """
    @swagger.doc({
        "summary":"Gets an individual object",
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
        "responses":{
            '200': {
                'description': 'Ok',
            }
        }
    }
    )
    def get(self, oid):
        result = query(session, AstroObject, None, None,
                       None, AstroObject.oid == oid)
        serializer = AstroObjectSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ObjectListResource(Resource):
    """
    Astro object list resource
    """
    @swagger.doc({
        "summary":"Gets a list of objects",
        "description":"long description",
        "responses":{
            '200': {
                'description': 'Ok',
            }
        }
    }
    )
    def get(self):
        result = query(session, AstroObject, 1, 1)
        serializer = AstroObjectSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)
