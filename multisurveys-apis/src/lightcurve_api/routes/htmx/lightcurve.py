import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lightcurve_api.services.lightcurve_plot_service import service as lightcurve_plot_service
from core.config.dependencies import db_dependency

router = APIRouter(prefix="/htmx")

templates = Jinja2Templates(
    directory="src/lightcurve_api/routes/htmx/templates",
    autoescape=True,
    auto_reload=True,
)

templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8001")


@router.get("/lightcurve", response_class=HTMLResponse)
def lightcurve(request: Request, oid: str, survey_id: str, db: db_dependency):
    result, config_state = lightcurve_plot_service.lightcurve_plot(oid, survey_id, db.session)
    return templates.TemplateResponse(
        name="lightcurve.html.jinja",
        context={"request": request, "options": result.echart_options, "config_state": config_state},
    )
