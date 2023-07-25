from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from .models import classifier_model, class_model
from flask_restx import Namespace, Resource
from dependency_injector.wiring import inject, Provide
from api.container import AppContainer

api = Namespace("classifier", description="Classifier routes")
api.models[classifier_model.name] = classifier_model
api.models[class_model.name] = class_model


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ClassifierList(Resource):
    @api.doc("classifier")
    @api.marshal_with(classifier_model)
    @inject
    def get(
        self, session_factory=Provide[AppContainer.psql_db.provided.session]
    ):
        """
        Gets all clasifiers
        """
        with session_factory() as session:
            classifiers = session.query(models.Taxonomy).all()
            return classifiers


@api.route("/<classifier_name>/<classifier_version>/classes")
@api.param("classifier_name", "The classifier's name")
@api.param("classifier_version", "Classifier's Version")
@api.response(200, "Success")
@api.response(404, "Classifier Not found")
class Classifier(Resource):
    @api.doc("get_classes")
    @api.marshal_list_with(class_model)
    @inject
    def get(
        self,
        classifier_name,
        classifier_version,
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        with session_factory() as session:
            classifier = (
                session.query(models.Taxonomy)
                .filter(models.Taxonomy.classifier_name == classifier_name)
                .filter(
                    models.Taxonomy.classifier_version == classifier_version
                )
                .one_or_none()
            )
            if classifier is not None:
                classes = [{"name": c} for c in classifier.classes]
                return classes
            else:
                raise NotFound
