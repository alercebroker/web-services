from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import Class
from api.db import session

class ClassSchema(Schema):
    type="object"
    resource_fields = {
        "name": fields.String,
        "acronym": fields.String
    }  


class ClassResource(Resource):
    """
    Class individual resource
    """
    @swagger.doc({
        "summary": "Gets an individual class",
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
                    "application/json": {
                        'schema': ClassSchema
                    }
                }
            }
        }
    }
    )
    def get(self, name):
        pass


class ClassListResource(Resource):
    """
    Class list resource
    """
    def get(self):
        pass