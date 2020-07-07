from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from db_plugins.db.sql import models
from .models import classification_model
from werkzeug.exceptions import NotFound
from ...db import db

api = Namespace("probabilities", description="Class probabilities related operations")
api.models[classification_model.name] = classification_model

@api.route("/<id>/probabilities")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Probabilities(Resource):
    @api.doc("probabilities")
    @api.marshal_list_with(classification_model)
    def get(self, id):
        obj = db.query(models.Object ).find_one(filter_by={"oid":id})
        if obj:
            return obj.classifications
        else:
            raise NotFound("Object not found")

