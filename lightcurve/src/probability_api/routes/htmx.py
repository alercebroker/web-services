import re
import os
import json
import pprint
from typing import Annotated
from fastapi import FastAPI, Request, Query

from core.services.object import get_probabilities,get_taxonomies
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from ..result_handler import handle_error, handle_success

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
    data_by_higher_version = {}

    """
        Dictionary format:
        {
            'lc_classifier': {
                                'hierarchical_rf_1.1.0: [{},{},{}]
                                }
        }
    """

    for itemKey, itemValue in prob_dict.items():
        if len(itemValue) > 1 :
            lastest_version = sorted(itemValue.keys())[-1]
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

def classifiers_options(taxonomy_dict, group_prob_by_version):
    class_dict = []
    priorities_arr = []
    non_priotities_arr = []
    priorities = {
    'lc_classifier': 0,
    'lc_classifier_top': 1,
    'stamp_classifier': 2,
    'LC_classifier_ATAT_forced_phot(beta)': 3,
    'LC_classifier_BHRF_forced_phot(beta)': 4,
    }

    for key, value in priorities.items():
        if key in group_prob_by_version:
            class_dict.append({ key : format_classifiers_name(key) })


    for key in group_prob_by_version.keys():
        if key not in priorities:
            non_priotities_arr.append({ key : format_classifiers_name(key) })

    class_dict = class_dict + non_priotities_arr

    return class_dict

def format_classifiers_name(classifier_name):
    return classifier_name.replace('_',' ').title()


@router.get("/probabilities/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):

    prob_list = get_probabilities(oid,session_factory = request.app.state.psql_session)
    taxonomy_list = get_taxonomies(session_factory = request.app.state.psql_session)

    taxonomy_dict = taxonomy_data(taxonomy_list)

    group_prob = group_data_by_classifier_dict(prob_list)
    group_prob_by_version = filter_data_by_higher_version(group_prob)
    
    class_options = classifiers_options(taxonomy_dict, group_prob_by_version)

    return templates.TemplateResponse(
      name='prob.html.jinja',
      context={'request': request,
               'taxonomy_dict': taxonomy_dict,
               'group_prob_dict': group_prob_by_version,
               'class_dict': class_options
               },
  )
