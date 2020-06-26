from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from ...db import db

api = Namespace("magstats", description="Magnitude Statistics related operations")

@api.route("/<id>/magstats")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class MagStats(Resource):
    def get(self, id):
        pass