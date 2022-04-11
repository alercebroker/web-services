from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql import models
from .models import magstats_model
from werkzeug.exceptions import NotFound
from ...database_access.psql_db import db

api = Namespace(
    "magnitude statistics",
    description="Magnitude Statistics related operations",
)
api.models[magstats_model.name] = magstats_model


@api.route("/<id>/magstats")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class MagStats(Resource):
    @api.doc("magstats")
    @api.marshal_list_with(magstats_model)
    def get(self, id):
        obj = (
            db.query(models.Object)
            .filter(models.Object.oid == id)
            .one_or_none()
        )
        if obj:
            return obj.magstats
        else:
            raise NotFound
