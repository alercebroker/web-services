from fastapi import APIRouter, Request
from fastapi import HTTPException
from core.idmapper.idmapper import parse_oid
from core.idmapper.survey_mapper import DEFAULT_SURVEY, Survey
from ..services.probability import get_classifier_id, get_classifiers, get_probability


router = APIRouter()


@router.get("/")
def ping():
    return "This is the probability API"


@router.get("/probability")
def probability(
    request: Request,
    oid: str,
    classifier: str | None = None,
    survey_id: Survey | None = None,
):
    master_id = parse_oid(survey_id, oid)
    session = request.app.state.psql_session

    if classifier:
        classifier_id = get_classifier_id(classifier, survey_id or DEFAULT_SURVEY, session_factory=session)
        if classifier_id is None:
            raise HTTPException(status_code=404, detail=f"Classifier '{classifier}' not found")
        classifiers_list = {classifier_id: classifier}
    else:
        classifiers_list = get_classifiers(session_factory=session)

    probability = get_probability(master_id, classifiers_list, survey_id or DEFAULT_SURVEY, session_factory=session)

    if not probability:
        raise HTTPException(status_code=404, detail="Probability not found for the given OID")

    return probability
