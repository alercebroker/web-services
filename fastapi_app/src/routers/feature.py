from fastapi import APIRouter

router = APIRouter(
    prefix="/features",
    tags=["features"],
)

@router.get("/")
async def get_features():
    return []