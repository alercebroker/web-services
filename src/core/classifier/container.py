from dependency_injector import containers, providers
from db_plugins.db.mongo.connection import MongoConnection

from .domain import ClassifierService
from . import infrastructure, use_case


class ClassifierContainer(containers.DeclarativeContainer):
    db = providers.Dependency(instance_of=MongoConnection)

    repo_classifiers = providers.Factory(
        infrastructure.ClassifiersRepository, db=db
    )
    repo_classes = providers.Factory(
        infrastructure.ClassesRepository, db=db
    )

    service = providers.Factory(
        ClassifierService,
        repo_classifiers=repo_classifiers,
        repo_classes=repo_classes,
    )

    get_classifiers = providers.Factory(
        use_case.GetClassifiers, service=service
    )
    get_classes = providers.Factory(
        use_case.GetClasses, service=service
    )
