from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import NonDetection
from db_plugins.db.sql.serializers import NonDetectionSchema
from api.app import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}

class ObjectResource(Resource):
    def get(self, oid, fid, datetime):
        result = query(session, NonDetection, None, None, None,
                       NonDetection.oid == oid,
                       NonDetection.fid == fid,
                       NonDetection.datetime == datetime)
        serializer = NonDetectionSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ObjectListResource(Resource):
    def get(self):
        result = query(session, NonDetection, 1, 1)
        serializer = NonDetectionSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)