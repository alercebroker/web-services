from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

router = APIRouter()

templates = Jinja2Templates(
    directory="./templates", autoescape=True, auto_reload=True
)

@router.get("/")
def root():
    return "this is the anomaly module"

@router.get("/grafico", response_class="HTMLResponse")
def grafico(request: Request):
    return templates.TemplateResponse(
        name="test_template.jinja.html",
        context={
            "request": request,
        },
    )

