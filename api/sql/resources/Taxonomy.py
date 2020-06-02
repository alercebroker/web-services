from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Taxonomy
from db_plugins.db.sql.serializers import TaxonomySchema

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}

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