from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_2 import Schema
from flask_restful_swagger_3 import swagger
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Class
from db_plugins.db.sql.serializers import ClassSchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}


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
        "requestBody:": {
            "content": {
                "/class/oid": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "description": "name of the class",
                                "type": "string"
                            },
                            "acronym": {
                                "description": "acronym of the class",
                                "type": "string"
                            },
                        },
                        "required": ["name"]
                    }
                }
            }
        },
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

    """
    def post(self, name):
        data = request.args
        response = put(session, data)
        return jsonify(response)
    """


class ClassListResource(Resource):
    """
    Class list resource
    """
    """
    @swagger.doc({
        "summary": "Gets a list of classes",
        "description": "long description",
        "requestBody:": {
            "content": {
                "/class": {
                    "schema": {
                        "type": "list",
                        "properties": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "name of the class",
                                    "type": "string"
                                },
                                "acronym": {
                                    "description": "acronym of the class",
                                    "type": "string"
                                },
                            },
                            "required": ["name"]
                        }
                    }
                }
            }
        },
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