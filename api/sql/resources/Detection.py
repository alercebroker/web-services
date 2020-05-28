from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Detection
from db_plugins.db.sql.serializers import DetectionSchema
from .. import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}

class DetectionResource(Resource):
    def get(self, candid):
        result = query(session, Detection, None, None, None, Detection.candid == candid)
        serializer = DetectionSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class DetectionListResource(Resource):
    def get(self):
        result = query(session, Detection, 1, 1)
        serializer = DetectionSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)