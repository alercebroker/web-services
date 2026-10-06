from fastapi import Request
from src.probability_api.services.frontend_services import get_classifiers_names_for_front
from ..services.probability import get_object_probability_model, get_probability_for_frontend
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.static_files import configure_templates


router = APIRouter()
templates = Jinja2Templates(directory="src/probability_api/templates", autoescape=True, auto_reload=True)
configure_templates(templates, "http://localhost:8004")


@router.get("/htmx/probabilities/{oid}", response_class=HTMLResponse)
def object_probability_app(
    request: Request,
    oid: str,
    survey: str,
):
    object_model = get_object_probability_model(
        oid,
        survey,
        request.app.state.psql_session,
    )

    probabilities = get_probability_for_frontend(
        object_model,
        session_factory=request.app.state.psql_session,
    )

    classifiers_names = get_classifiers_names_for_front(object_model, probabilities)

    return templates.TemplateResponse(
        name="prob.html.jinja",
        context={
            "request": request,
            "group_prob_dict": probabilities,
            "class_dict": classifiers_names,
        },
    )
