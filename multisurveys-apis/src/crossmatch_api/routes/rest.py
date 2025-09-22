from fastapi import APIRouter
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True)


@router.get("/")
def root():
    return "This is the crossmatch API"


@router.get("/healthcheck")
def healthcheck():
    return "OK"
