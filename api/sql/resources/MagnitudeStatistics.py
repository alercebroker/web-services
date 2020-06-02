from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from db_plugins.db.sql import query
from db_plugins.db.sql.models import MagnitudeStatistics
from db_plugins.db.sql.serializers import MagnitudeStatisticsSchema
from .. import session

parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}

class MagnitudesResource(Resource):
    def get(self, oid, magnitude_type, fid):
        result = query(session, MagnitudeStatistics, None, None, None,
                       MagnitudeStatistics.oid == oid,
                       MagnitudeStatistics.magnitude_type == magnitude_type
        )
        serializer = MagnitudeStatisticsSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class MagnitudesListResource(Resource):
    def get(self):
        result = query(session, MagnitudeStatistics, 1, 1)
        serializer = MagnitudeStatisticsSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)