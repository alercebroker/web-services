from fastapi import APIRouter

router = APIRouter(
    prefix="/classifiers",
    tags=["classifiers"],
)

@router.get("/")
async def get_classifiers():
    return []