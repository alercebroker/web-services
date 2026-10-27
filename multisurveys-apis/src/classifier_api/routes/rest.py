from fastapi import APIRouter, Request
from fastapi import HTTPException
from core.idmapper.survey_mapper import get_survey_id
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
    survey_id: str | None = None,
):
    """Every classifier with its classes, as a list. Filter by `classifier_name` and by `survey_id` (`ztf` or `lsst`)."""
    session = request.app.state.psql_session
    sid = get_survey_id(survey_id) if survey_id is not None else None

    if classifier_name:
        classifiers = get_classifier_by_name(classifier_name, session_factory=session)
        if len(classifiers) == 0:
            raise HTTPException(status_code=404, detail=f"Classifier '{classifier_name}' not found")
    else:
        classifiers = get_classifiers(session_factory=session)

    if sid is not None:
        classifiers = [classifier for classifier in classifiers if classifier.survey_id == sid]

    return classifiers


@router.get("/classes", summary="Classes of a classifier version")
def classes(request: Request, classifier_name: str, classifier_version: str, survey_id: str | None = None):
    """The classes a classifier version can assign, in taxonomy order, as `[{"name": ...}]`.

    Give `survey_id` (`ztf` or `lsst`) when the same classifier name and version exist for both surveys.
    """
    sid = get_survey_id(survey_id) if survey_id is not None else None
    class_names = get_classes(
        classifier_name, classifier_version, session_factory=request.app.state.psql_session, sid=sid
    )

    if class_names is None:
        raise HTTPException(
            status_code=404,
            detail=f"Classifier '{classifier_name}' version '{classifier_version}' not found",
        )

    return [{"name": class_name} for class_name in class_names]
