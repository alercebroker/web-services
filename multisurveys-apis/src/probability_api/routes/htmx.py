import os
from fastapi import Request

from ..services.probability import get_probability, get_classifiers
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .test_prob import probability_parser

router = APIRouter()
templates = Jinja2Templates(directory="src/probability_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8004")


def taxonomy_data(taxonomy_list):
    """
    dict example: {classifier_name:{class_name:[],classifier_version:''}}
    """

    taxonomy_dict = {}

    for n in range(len(taxonomy_list)):
        taxonomy_dict[taxonomy_list[n].classifier_name] = taxonomy_list[n].__dict__

    return taxonomy_dict


def filter_data_by_higher_version(prob_dict):
    """
    Dictionary format: {'classifier_name': {'classifier_version: [{},{},{}]}}
    """
    data_by_higher_version = {}

    for itemKey, itemValue in prob_dict.items():
        if len(itemValue) > 1:
            lastest_version = max(itemValue.keys())
            if itemKey not in data_by_higher_version:
                data_by_higher_version[itemKey] = {lastest_version: itemValue[lastest_version]}
        else:
            if itemKey not in data_by_higher_version:
                data_by_higher_version[itemKey] = itemValue

    return data_by_higher_version


def group_data_by_classifier_dict(prob_lis):
    group_data_by_classifier = {}

    for item in prob_lis:
        aux_dict = {
            "classifier_name": item.classifier_name,
            "classifier_version": item.classifier_version,
            "class_name": item.class_name,
            "probability": item.probability,
            "ranking": item.ranking,
        }
        classifier_name = item.classifier_name
        classifier_version = item.classifier_version

        if item.classifier_name not in group_data_by_classifier:
            group_data_by_classifier[classifier_name] = {}

        if classifier_version not in group_data_by_classifier[classifier_name]:
            group_data_by_classifier[classifier_name][classifier_version] = []

        group_data_by_classifier[classifier_name][classifier_version].append(aux_dict)

    return group_data_by_classifier


def classifiers_options(group_prob_by_version):
    class_dict = []
    priorities = {
        "lc_classifier": 0,
        "lc_classifier_top": 1,
        "lc_classifier_BHRF_forced_phot": 2,
        "stamp_classifier": 3,
        "LC_classifier_ATAT_forced_phot(beta)": 4,
        "stamp_classifier_2025_beta": 5,
    }

    for key, value in priorities.items():
        if key in group_prob_by_version:
            class_dict.append({key: format_classifiers_name(key)})

    return class_dict


def format_classifiers_name(classifier_name):
    classifier_name = classifier_name.replace("_", " ").title()

    if classifier_name.find("Atat") != -1:
        classifier_name = classifier_name.replace("Atat", "ATAT")
    if classifier_name.find("Bhrf") != -1:
        classifier_name = classifier_name.replace("Bhrf", "BHRF")

    return classifier_name

def lsst_classfiers_parser(classifier_list):
    
    parsed_classifier = {}

    accepted_lsst_classifiers = ["stamp_classifier_rubin"]
   
    for k,v in classifier_list.items():
        if v in accepted_lsst_classifiers:
            parsed_classifier[k] = v

    return parsed_classifier


@router.get("/htmx/probabilities/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):
    classifier_list = get_classifiers(
        session_factory=request.app.state.psql_session
    )  # classifier_list es un diccionario
    classifier_list = lsst_classfiers_parser(classifier_list)
    class_options = [{v: v} for k, v in classifier_list.items()]
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
