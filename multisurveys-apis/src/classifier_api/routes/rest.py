from fastapi import APIRouter, Request
from fastapi import HTTPException
from ..services.classifiers import get_classifier_by_name, get_classifiers

router = APIRouter()


@router.get("/")
async def ping():
    return "This is the classifier API"


@router.get("/classifiers")
async def classifiers(
    request: Request,
    classifier_name: str | None = None,
):
    if classifier_name:
        classifiers = get_classifier_by_name(
            classifier_name, session_factory=request.app.state.psql_session
        )

        if len(classifiers) == 0:
            raise HTTPException(
                status_code=404,
                detail="Classifier not found for the given OID",
            )

        classifiers = classifiers[
            0
        ]  # Assuming get_classifier_by_name returns a list, we take the first one

    else:
        classifiers = get_classifiers(session_factory=request.app.state.psql_session)

    return classifiers
