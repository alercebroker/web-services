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
def grafico(request: Request, page: int = 1, per_page: int = 10):

    data = [
        {
            "oid": "oid_001",
            "ndet": 10,
            "firstMJD": 59100.5,
            "lastMJD": 59130.5,
            "score_transcient": 0.85,
            "score_stochastic": 0.70,
            "score_periodic": 0.65
        },
        {
            "oid": "oid_002",
            "ndet": 15,
            "firstMJD": 59105.7,
            "lastMJD": 59135.8,
            "score_transcient": 0.75,
            "score_stochastic": 0.80,
            "score_periodic": 0.60
        },
        {
            "oid": "oid_003",
            "ndet": 8,
            "firstMJD": 59110.0,
            "lastMJD": 59125.9,
            "score_transcient": 0.90,
            "score_stochastic": 0.65,
            "score_periodic": 0.70
        },
        {
            "oid": "oid_004",
            "ndet": 12,
            "firstMJD": 59120.4,
            "lastMJD": 59140.6,
            "score_transcient": 0.88,
            "score_stochastic": 0.72,
            "score_periodic": 0.75
        },
        {
            "oid": "oid_005",
            "ndet": 9,
            "firstMJD": 59122.5,
            "lastMJD": 59132.1,
            "score_transcient": 0.80,
            "score_stochastic": 0.78,
            "score_periodic": 0.68
        },
        {
            "oid": "oid_006",
            "ndet": 14,
            "firstMJD": 59118.3,
            "lastMJD": 59138.2,
            "score_transcient": 0.92,
            "score_stochastic": 0.68,
            "score_periodic": 0.63
        },
        {
            "oid": "oid_007",
            "ndet": 11,
            "firstMJD": 59113.6,
            "lastMJD": 59133.4,
            "score_transcient": 0.77,
            "score_stochastic": 0.75,
            "score_periodic": 0.70
        },
        {
            "oid": "oid_008",
            "ndet": 13,
            "firstMJD": 59126.0,
            "lastMJD": 59146.7,
            "score_transcient": 0.85,
            "score_stochastic": 0.70,
            "score_periodic": 0.66
        },
        {
            "oid": "oid_009",
            "ndet": 10,
            "firstMJD": 59115.8,
            "lastMJD": 59136.3,
            "score_transcient": 0.89,
            "score_stochastic": 0.73,
            "score_periodic": 0.65
        },
        {
            "oid": "oid_010",
            "ndet": 16,
            "firstMJD": 59109.2,
            "lastMJD": 59129.1,
            "score_transcient": 0.82,
            "score_stochastic": 0.77,
            "score_periodic": 0.62
        },
        {
            "oid": "oid_011",
            "ndet": 7,
            "firstMJD": 59124.4,
            "lastMJD": 59144.5,
            "score_transcient": 0.87,
            "score_stochastic": 0.79,
            "score_periodic": 0.67
        },
        {
            "oid": "oid_012",
            "ndet": 14,
            "firstMJD": 59117.1,
            "lastMJD": 59137.6,
            "score_transcient": 0.83,
            "score_stochastic": 0.74,
            "score_periodic": 0.71
        },
        {
            "oid": "oid_013",
            "ndet": 9,
            "firstMJD": 59116.2,
            "lastMJD": 59136.9,
            "score_transcient": 0.81,
            "score_stochastic": 0.70,
            "score_periodic": 0.64
        },
        {
            "oid": "oid_014",
            "ndet": 12,
            "firstMJD": 59119.9,
            "lastMJD": 59139.7,
            "score_transcient": 0.78,
            "score_stochastic": 0.76,
            "score_periodic": 0.68
        },
        {
            "oid": "oid_015",
            "ndet": 10,
            "firstMJD": 59114.3,
            "lastMJD": 59134.2,
            "score_transcient": 0.88,
            "score_stochastic": 0.72,
            "score_periodic": 0.73
        },
        {
            "oid": "oid_016",
            "ndet": 11,
            "firstMJD": 59121.8,
            "lastMJD": 59141.4,
            "score_transcient": 0.86,
            "score_stochastic": 0.78,
            "score_periodic": 0.69
        },
        {
            "oid": "oid_017",
            "ndet": 8,
            "firstMJD": 59111.7,
            "lastMJD": 59131.9,
            "score_transcient": 0.80,
            "score_stochastic": 0.74,
            "score_periodic": 0.70
        },
        {
            "oid": "oid_018",
            "ndet": 13,
            "firstMJD": 59123.5,
            "lastMJD": 59143.3,
            "score_transcient": 0.84,
            "score_stochastic": 0.71,
            "score_periodic": 0.66
        },
        {
            "oid": "oid_019",
            "ndet": 9,
            "firstMJD": 59112.9,
            "lastMJD": 59132.6,
            "score_transcient": 0.79,
            "score_stochastic": 0.75,
            "score_periodic": 0.65
        },
        {
            "oid": "oid_020",
            "ndet": 15,
            "firstMJD": 59108.5,
            "lastMJD": 59128.7,
            "score_transcient": 0.82,
            "score_stochastic": 0.77,
            "score_periodic": 0.62
        }
    ]

    
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = len(data)/per_page

    paginated_data = data[start:end]

    return templates.TemplateResponse(
        name="table_template.html.jinja",
        context={
            "request": request,
            "data": paginated_data,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total": len(data),
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


