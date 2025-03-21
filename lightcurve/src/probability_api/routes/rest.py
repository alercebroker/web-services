import re
import os
from typing import Annotated
from fastapi import Query

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(
    directory="src/api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)

@router.get("/")
def root():
    return "this is the probability module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"

