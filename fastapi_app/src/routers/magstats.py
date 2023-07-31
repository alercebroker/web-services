from fastapi import APIRouter

router = APIRouter(
    prefix="/magstats",
    tags=["magstats"],
)

@router.get("/")
async def get_magstats():
    return []