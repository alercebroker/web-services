from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def ping():
    return "This is the Aladin API"


@router.get("/healthcheck")
def healthcheck():
    return "OK"
