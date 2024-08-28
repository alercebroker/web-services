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

@router.get("/tabla", response_class="HTMLResponse")
def grafico(request: Request):

    data =[
        {
            "oid": "example_oid_1",
            "ndet": 1,
            "firstMJD": 59123.1,
            "lastMJD": 59124.1,
            "score_transcient": 0.85,
            "score_stochastic": 0.75,
            "score_periodic": 0.65
        },
        {
            "oid": "example_oid_2",
            "ndet": 2,
            "firstMJD": 59125.1,
            "lastMJD": 59126.1,
            "score_transcient": 0.88,
            "score_stochastic": 0.78,
            "score_periodic": 0.68
        }
    ]

    return templates.TemplateResponse(
        name="table_template.html.jinja",
        context={
            "request": request,
            "data": data,
        },
    )



@router.get("/detalles", response_class="HTMLResponse")
def grafico(request: Request):
    return templates.TemplateResponse(
        name="details_template.html.jinja",
        context={
            "request": request,
        },
    )


