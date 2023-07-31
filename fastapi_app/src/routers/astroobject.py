from fastapi import APIRouter

router = APIRouter(
    prefix="/objects",
    tags=["objects"],
)

@router.get("/")
async def get_objects():
    return []