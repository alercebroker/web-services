from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import Taxonomy
from db_plugins.db.sql.serializers import TaxonomySchema
from api.db import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')


class TaxonomyModel(Schema):
    type = 'object'
    resource_fields = {
        "name": fields.String
    }


class TaxnomyResponseModel(Schema):
    type = 'array'
    items = TaxonomyModel


class TaxonomyResource(Resource):
    def get(self, name):
        result = query(session, Taxonomy, None, None, None, Taxonomy.name == name)
        serializer = TaxonomySchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class TaxonomyListResource(Resource):
    def get(self):
        result = query(session, Taxonomy, 1, 1)
        serializer = TaxonomySchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)