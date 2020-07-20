from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from ...db import db
from .models import class_model
from flask_restx import Namespace, Resource

api = Namespace("classes", description="Classes")
api.models[class_model.name] = class_model


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class Class(Resource):
    @api.doc("class")
    @api.marshal_with(class_model)
    def get(self):
        """
        Gets all classes
        """
        classes = db.query(models.Class).all()
        if len(classes):
            return classes
        else:
            raise NotFound
