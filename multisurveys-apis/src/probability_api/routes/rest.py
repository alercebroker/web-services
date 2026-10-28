from fastapi import APIRouter, Request
from fastapi import HTTPException
from core.idmapper.idmapper import parse_oid
from core.idmapper.survey_mapper import Survey
from ..services.probability import get_probability, get_classifiers


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

    classifiers_list = get_classifiers(session_factory=request.app.state.psql_session)

    if classifier:
        ids_by_name = {name: classifier_id for classifier_id, name in classifiers_list.items()}
        classifier_id = ids_by_name.get(classifier)
        if classifier_id is None:
            raise HTTPException(status_code=404, detail=f"Classifier '{classifier}' not found")
        classifiers_list = {classifier_id: classifier}

    probability = get_probability(master_id, classifiers_list, session_factory=request.app.state.psql_session)

    if not probability:
        raise HTTPException(status_code=404, detail="Probability not found for the given OID")

    return probability
