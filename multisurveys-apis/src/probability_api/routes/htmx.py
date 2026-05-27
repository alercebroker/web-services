import os
from fastapi import Request

from ..services.probability import get_probability, get_classifiers
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .test_prob import probability_parser
from ..services.lsst_service import classifier_name_parser, sort_classifiers

router = APIRouter()
templates = Jinja2Templates(directory="src/probability_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8004")


@router.get("/htmx/probabilities/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):
    classifier_list = get_classifiers( session_factory=request.app.state.psql_session )
    classifier_list = sort_classifiers(classifier_list)
    class_options = classifier_name_parser(classifier_list)
    
    prob_list = get_probability(oid, classifier_list, session_factory=request.app.state.psql_session)
    group_prob = probability_parser(prob_list)
    
    
    return templates.TemplateResponse(
        name="prob.html.jinja",
        context={
            "request": request,
            "group_prob_dict": group_prob,
            "class_dict": class_options,
        },
    )
