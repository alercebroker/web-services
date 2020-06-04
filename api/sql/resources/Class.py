from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Class
from db_plugins.db.sql.serializers import ClassSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both

class ClassModel(Schema):
    pass


class ClassResource(Resource):
    """
    Class individual resource
    """
    """
    @swagger.doc({
        "summary": "Gets an individual object",
        "description": "long description",
        "parameters": [
            {
                "name": "name",
                "in": "path",
                "description": "Name of the class",
                "required": True,
                "schema":{
                    "type": "string"
                }
            }
        ],
        "responses": {
            '200': {
                'description': 'Class got',
                'content': {
                    "application/json": {}
                }
            }
        }
    }
    )
    """
    def get(self, name):
        result = query(session, Class, None, None, None, Class.name == name)
        serializer = ClassSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ClassListResource(Resource):
    """
    Class list resource
    """
    """
    @swagger.doc({
        "summary": "Gets a list of classes",
        "description": "long description",
        "responses": {
            '200': {
                'description': 'Class got',
                'content': {
                    "application/json": {}
                }
            }
        }
    }
    )
    """
    def get(self):
        result = query(session, Class, 1, 1)
        serializer = ClassSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)