import os
import pprint
from fastapi import FastAPI, Request, Query

# from core.services.object import get_probabilities, get_taxonomies
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from core.repository.dummy_data import classifiers_probabilities_dict, classifiers_options_dicts

router = APIRouter()
templates = Jinja2Templates(
    directory="src/probability_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8004"
)


def taxonomy_data(taxonomy_list):
    """
        dict example: {classifier_name:{class_name:[],classifier_version:''}}
    """
    
    taxonomy_dict  = {}

    for n in range(len(taxonomy_list)):
        taxonomy_dict[taxonomy_list[n].classifier_name] = taxonomy_list[n].__dict__

    return taxonomy_dict


def filter_data_by_higher_version(prob_dict):

    """
        Dictionary format: {'classifier_name': {'classifier_version: [{},{},{}]}}
    """
    data_by_higher_version = {}

    for itemKey, itemValue in prob_dict.items():
        if len(itemValue) > 1 :
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
        'classifier_name': item.classifier_name,
        'classifier_version': item.classifier_version,
        'class_name': item.class_name,
        'probability': item.probability,
        'ranking': item.ranking,
        }
        classifier_name = item.classifier_name
        classifier_version = item.classifier_version

        if item.classifier_name not in group_data_by_classifier:
            group_data_by_classifier[classifier_name] = {}
        
        if classifier_version not in group_data_by_classifier[classifier_name]:
            group_data_by_classifier[classifier_name][classifier_version]= []

        group_data_by_classifier[classifier_name][classifier_version].append(aux_dict)

    return group_data_by_classifier

def classifiers_options(group_prob_by_version):
    class_dict = []
    priorities = {
    'lc_classifier': 0,
    'lc_classifier_top': 1,
    'lc_classifier_BHRF_forced_phot': 2,
    'stamp_classifier': 3,
    'LC_classifier_ATAT_forced_phot(beta)': 4,
    'stamp_classifier_2025_beta': 5,
    }

    for key, value in priorities.items():
        if key in group_prob_by_version:
            class_dict.append({ key : format_classifiers_name(key) })

    return class_dict

def format_classifiers_name(classifier_name):
    classifier_name = classifier_name.replace('_',' ').title()

    if classifier_name.find('Atat') != -1:
        classifier_name = classifier_name.replace("Atat", "ATAT")
    if classifier_name.find('Bhrf') != -1:
        classifier_name = classifier_name.replace("Bhrf", "BHRF")

    return classifier_name


@router.get("/probabilities/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):

    # prob_list = get_probabilities(oid,session_factory = request.app.state.psql_session)
    # taxonomy_list = get_taxonomies(session_factory = request.app.state.psql_session)

    # taxonomy_dict = taxonomy_data(taxonomy_list)

    # group_prob = group_data_by_classifier_dict(prob_list)
    # group_prob_by_version = filter_data_by_higher_version(group_prob)
    
    # class_options = classifiers_options(group_prob_by_version)

    group_prob = classifiers_probabilities_dict
    class_options = classifiers_options_dicts

    return templates.TemplateResponse(
      name='prob.html.jinja',
      context={
            'request': request,
            'group_prob_dict': group_prob,
            'class_dict' : class_options
        },
  )
