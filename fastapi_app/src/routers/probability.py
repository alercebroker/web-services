from fastapi import APIRouter

router = APIRouter(
    prefix="/probabilities",
    tags=["probabilities"],
)

@router.get("/")
async def get_probabilities():
    return []