from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.exceptions import ObjectNotFound
from ..get_crossmatch_data import get_alerce_data


router = APIRouter()
templates = Jinja2Templates(
    directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True
)

@router.get("/")
def root():
    return "This is the crossmatch API"


@router.get("/healthcheck")
def healthcheck():
    return "OK"
