from fastapi import Request

from ..services.probability import get_probability, get_classifiers
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from core.static_files import configure_templates
from fastapi.responses import HTMLResponse
from ..services.parser import parse_grouped_probabilities
from ..services.lsst_service import classifier_name_parser, sort_classifiers, priorities_by_survey
from core.idmapper.idmapper import encode_ids

router = APIRouter()
templates = Jinja2Templates(directory="src/probability_api/templates", autoescape=True, auto_reload=True)
configure_templates(templates, "http://localhost:8004")

import pprint
@router.get("/htmx/probabilities/{oid}", response_class=HTMLResponse)
def object_probability_app(
    request: Request,
    oid: str,
    survey: str,
):
    master_id = encode_ids(survey, [oid])

    classifier_list = get_classifiers(session_factory=request.app.state.psql_session)
    prob_list = get_probability(int(master_id[0]), classifier_list, session_factory=request.app.state.psql_session)
    group_prob = parse_grouped_probabilities(prob_list)

    priorities = priorities_by_survey(survey)

    classifiers_sorted = [None] * 10
    for priority, index in priorities.items():
        if priority in classifier_list:
            classifiers_sorted[index] = classifier_list[priority]

    clean_classifiers = [classifier for classifier in classifiers_sorted if classifier is not None]


    filter_classifiers = [c for c in clean_classifiers if c in group_prob.keys()]

    result_arr = []
    for classifier_name in filter_classifiers:
        parsed_name = classifier_name.replace("_", " ").title()
        aux_dict = {classifier_name: parsed_name}
        result_arr.append(aux_dict)

    print("result_arr: ", result_arr)
    return templates.TemplateResponse(
        name="prob.html.jinja",
        context={
            "request": request,
            "group_prob_dict": group_prob,
            "class_dict": result_arr,
        },
    )
