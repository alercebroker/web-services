from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from ...db import db
from .models import classifier_model
from ..classes.models import class_model
from flask_restx import Namespace, Resource

api = Namespace("classifier", description="Classifier routes")
api.models[classifier_model.name] = classifier_model


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ClassifierList(Resource):
    @api.doc("classifier")
    @api.marshal_with(classifier_model)
    def get(self):
        """
        Gets all clasifiers
        """
        # classifiers = db.query(models.Classifier).all()
        classifiers = [{"name": "lc_classifier"}]
        if len(classifiers):
            return classifiers
        else:
            raise NotFound


@api.route("/<classifier_name>/classes")
@api.param("classifier_name", "The classifier's name")
@api.response(200, "Success")
@api.response(404, "Classifier Not found")
class Classifier(Resource):
    @api.doc("get_classes")
    @api.marshal_list_with(class_model)
    def get(self, classifier_name):
        # classifier = (
        #     db.query(models.Classifier)
        #     .filter(models.Classifier.name == classifier_name)
        #     .one_or_none()
        # )

        # if not classifier:
        #     raise NotFound

        # taxonomies = db.query(models.Taxonomy).filter(
        #     models.Taxonomy.name == classifier.taxonomy_name
        # ).all()

        # classes = []
        # for taxonomy in taxonomies:
        #     for _class in taxonomy.classes:
        #         classes.append(_class)
        classes = {
            "Light Curve": [
                {"name": "Active Galactic Nuclei", "acronym": "AGN"},
                {"name": "Blazar", "acronym": "Blazar"},
                {"name": "CV/Nova", "acronym": "CV/Nova"},
                {"name": "QSO", "acronym": "QSO"},
                {"name": "YSO", "acronym": "YSO"},
                {"name": "SLSN", "acronym": "SLSN"},
                {"name": "SNII", "acronym": "SNII"},
                {"name": "SNIa", "acronym": "SNIa"},
                {"name": "SNIbc", "acronym": "SNIbc"},
                {"name": "CEP", "acronym": "CEP"},
                {"name": "E", "acronym": "E"},
                {"name": "Long Period Variable", "acronym": "LPV"},
                {"name": "Periodic", "acronym": "Periodic"},
                {"name": "Stochastic", "acronym": "Stochastic"},
                {"name": "Transient", "acronym": "Transient"},
            ],
            "Stamp": [
                {"name": "Active Galactic Nuclei", "acronym": "AGN"},
                {"name": "Super Nova", "acronym": "SN"},
                {"name": "Variable Star", "acronym": "VS"},
                {"name": "Asteroid", "acronym": "Asteroid"},
                {"name": "Bogus", "acronym": "Bogus"},
            ],
        }
        return classes[classifier_name]
