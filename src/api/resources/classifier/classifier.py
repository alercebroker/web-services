from dependency_injector.providers import Factory
from dependency_injector.wiring import inject, Provide
from flask_restx import Namespace, Resource

from api.container import AppContainer
from core.classifier.domain import ClassifiersPayload
from shared.interface.command import Command, ResultHandler

from . import models

api = Namespace("classifier", description="Classifier routes")
api.models[models.classifiers] = models.classifiers
api.models[models.classes] = models.classes


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ClassifierList(Resource):
    @api.doc("classifier")
    @api.marshal_with(models.classifiers)
    @inject
    def get(self,
            command_factory: Factory[Command] = Provide[
                AppContainer.classifier_package.get_classifiers.provider
            ],
            result_handler: ResultHandler = Provide[
                AppContainer.view_result_handler
            ],
            ):
        """
        Gets all classifiers
        """
        command = command_factory(
            payload=ClassifiersPayload(),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result


@api.route("/<classifier_name>/<classifier_version>/classes")
@api.param("classifier_name", "The classifier's name")
@api.param("classifier_version", "Classifier's Version")
@api.response(200, "Success")
@api.response(404, "Classifier Not found")
class Classifier(Resource):
    @api.doc("get_classes")
    @api.marshal_list_with(models.classes)
    @inject
    def get(
        self,
        classifier_name,
        classifier_version,
        command_factory: Factory[Command] = Provide[
            AppContainer.classifier_package.get_classes.provider
        ],
        result_handler: ResultHandler = Provide[
            AppContainer.view_result_handler
        ],
    ):
        command = command_factory(
            payload=ClassifiersPayload(classifier_name=classifier_name,
                                       classifier_version=classifier_version),
            handler=result_handler,
        )
        command.execute()
        return result_handler.result
