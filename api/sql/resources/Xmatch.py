from flask_restful import fields, marshal_with, reqparse, Resource, marshal
from flask import jsonify
from flask_restful_swagger_3 import swagger, Schema
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Xmatch
from .. import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], type="string", dest='oid')


class LinksModel(Schema):
    type = 'object'
    # properties = {
    #     "x": {"type": "string"},
    #     "y": {"type": "string"}
    # }
    resource_fields ={
        "x": fields.String,
        "y": fields.String
    }


class XmatchModel(Schema):
    type = 'object'
    resource_fields = {
        "oid": fields.String(),
        "catid": fields.String(attribute="catalog_id"),
        "oid_catalog": fields.String(attribute="object_id_catalog"),
        "dist": fields.Float(attribute="distance"),
        "class_catalog": fields.String,
        "period": fields.Float,
        "links": fields.Nested(LinksModel.resource_fields),
    }
    # properties = {
    #     "oid": {"type": "string"},
    #     "links": LinksModel
    # }



class XmatchResource(Resource):
    @swagger.doc({
        "summary": "Gets xmatch information of an object",
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
                'description': 'Query successfully returns a xmatch item for the specified object id',
                'content': {
                    'application/json': {
                        'schema': XmatchModel
                    }
                }
            }
        }
    })
    @marshal_with(XmatchModel.resource_fields, envelope="resource")
    def get(self, oid):
        pass