from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Classifier
from db_plugins.db.sql.serializers import ClassifierSchema
from api.app import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}

class ObjectResource(Resource):
    def get(self, name):
        result = query(session, Classifier, None, None, None, Classifier.name == name)
        serializer = ClassifierSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ObjectListResource(Resource):
    def get(self):
        result = query(session, Classifier, 1, 1)
        serializer = ClassifierSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)