from fastapi import APIRouter, Request
from fastapi import HTTPException
from core.idmapper.idmapper import parse_oid
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
    survey_id: str | None = None,
):
    master_id = parse_oid(survey_id, oid)  # a bad oid is a ValueError: 400 from the central handler

    classifiers_list = get_classifiers(session_factory=request.app.state.psql_session)

    if classifier:
        for key, value in classifiers_list.items():
            if value == classifier:
                classifiers_list = {key: value}
                break
        if len(classifiers_list) != 1:
            raise HTTPException(status_code=404, detail="Classifier not found")

    probability = get_probability(master_id, classifiers_list, session_factory=request.app.state.psql_session)

    if not probability:
        raise HTTPException(status_code=404, detail="Probability not found for the given OID")

    return probability
