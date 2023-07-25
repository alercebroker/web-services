from fastapi import APIRouter

router = APIRouter(
    prefix="/lightcurve",
    tags=["lightcurve"],
)

@router.get("/")
async def get_lightcurve():
    return []