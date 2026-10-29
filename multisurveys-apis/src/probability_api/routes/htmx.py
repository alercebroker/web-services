from fastapi import Request
from src.probability_api.services.frontend_services import get_classifiers_names_for_front
from ..services.probability import get_object_probability_model, get_probability_for_frontend
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from core.static_files import configure_templates, html_templates
from core.idmapper.survey_mapper import Survey


router = APIRouter()
templates = html_templates("src/probability_api/templates")
configure_templates(templates, "http://localhost:8004")


@router.get("/htmx/probabilities/{oid}", response_class=HTMLResponse)
def object_probability_app(
    request: Request,
    oid: str,
    survey: Survey,
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
        request=request,
        name="prob.html.jinja",
        context={
            "request": request,
            "group_prob_dict": probabilities,
            "classifiers_names": classifiers_names,
        },
    )
