import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

router = APIRouter()

templates = Jinja2Templates(
    directory="./src/anomaly_api/templates", autoescape=True, auto_reload=True
)

templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)


@router.get("/")
def root():
    return "this is the anomaly module"

@router.get("/grafico", response_class="HTMLResponse")
def grafico(request: Request):
    return templates.TemplateResponse(
        name="anomaly_template.html.jinja",
        context={
            "request": request,
        },
    )

