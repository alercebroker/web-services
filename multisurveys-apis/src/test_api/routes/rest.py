from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return "this is a dummy module"
