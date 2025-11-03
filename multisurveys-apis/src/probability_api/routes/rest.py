from fastapi import APIRouter, Request
from fastapi import HTTPException
from ..services.probability import get_probability, get_classifiers


router = APIRouter()


@router.get("/")
async def ping():
    return "This is the probability API"


@router.get("/probability")
async def probability(
    request: Request,
    oid: str,
    classifier: str | None = None,
):
    classifiers_list = get_classifiers(session_factory=request.app.state.psql_session)

    if classifier:
        for key, value in classifiers_list.items():
            if value == classifier:
                classifiers_list = {key: value}
                break
        if len(classifiers_list) != 1:
            raise HTTPException(status_code=404, detail="Classifier not found")

    probability = get_probability(
        oid, classifiers_list, session_factory=request.app.state.psql_session
    )

    if not probability:
        raise HTTPException(
            status_code=404, detail="Probability not found for the given OID"
        )

    return probability
