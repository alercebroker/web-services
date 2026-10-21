from fastapi import APIRouter, Request
from fastapi import HTTPException
from core.repository.queries.classifiers import get_classes
from ..services.classifiers import get_classifier_by_name, get_classifiers

router = APIRouter()


@router.get("/")
def ping():
    return "This is the classifier API"


@router.get("/classifiers")
def classifiers(
    request: Request,
    classifier_name: str | None = None,
):
    if classifier_name:
        classifiers = get_classifier_by_name(classifier_name, session_factory=request.app.state.psql_session)

        if len(classifiers) == 0:
            raise HTTPException(
                status_code=404,
                detail="Classifier not found for the given OID",
            )

        classifiers = classifiers[0]  # Assuming get_classifier_by_name returns a list, we take the first one

    else:
        classifiers = get_classifiers(session_factory=request.app.state.psql_session)

    return classifiers


@router.get("/classes", summary="Classes of a classifier version")
def classes(request: Request, classifier_name: str, classifier_version: str):
    """The classes a classifier version can assign, in taxonomy order, as `[{"name": ...}]`."""
    class_names = get_classes(classifier_name, classifier_version, session_factory=request.app.state.psql_session)

    if class_names is None:
        raise HTTPException(
            status_code=404,
            detail=f"Classifier '{classifier_name}' version '{classifier_version}' not found",
        )

    return [{"name": class_name} for class_name in class_names]
