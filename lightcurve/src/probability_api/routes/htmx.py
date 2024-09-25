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

def prob_filter(prob_list, taxonomy_list):

    prob_dict = {}
    taxonomy_dict  = {}

    for n in range(len(taxonomy_list)):
        taxonomy_dict[f'tax_{n+1}'] = taxonomy_list[n].__dict__

    for k in range(len(prob_list)):
        prob_dict[f'prob_{k+1}'] = prob_list[k].__dict__

    return taxonomy_dict, prob_dict

def filter_classifier_name_taxonomy(taxonomy_dict):
    filter = ["lc_classifier", "lc_classifier_top", "stamp_classifier", "LC_classifier_BHRF_forced_phot(beta)", "LC_classifier_ATAT_forced_phot(beta)"]
    pop_keys = []
    for value in taxonomy_dict.keys():
        if(taxonomy_dict[value]["classifier_name"] in filter):
           pass
        else:
            pop_keys.append(value)

    for x in range(len(pop_keys)):
        taxonomy_dict.pop(pop_keys[x])
    
    taxonomy_dict = eliminated_duplicates_by_higher_version(taxonomy_dict)
    
    return taxonomy_dict

def eliminated_duplicates_by_higher_version(taxonomy_dict):
    # format of dict: {classifier_name: key}
    seen_classifiers = {}
    filtered_taxonomy = {}
    
    for key, value in taxonomy_dict.items():
        classifier_name = value["classifier_name"]
        if classifier_name not in seen_classifiers:
            filtered_taxonomy[key] = value
            seen_classifiers[classifier_name] = key
        else:
            oldKey = seen_classifiers[classifier_name]
            if value["classifier_version"] > taxonomy_dict[oldKey]["classifier_version"]:
                filtered_taxonomy.pop(oldKey)
                filtered_taxonomy[key] = value
                seen_classifiers[classifier_name] = key

    return filtered_taxonomy

def group_data_by_classifier(prob_dict):
    classifiers_names = ["lc_classifier", "lc_classifier_top", "stamp_classifier", "LC_classifier_BHRF_forced_phot(beta)", "LC_classifier_ATAT_forced_phot(beta)"]
    group_data_dict = {}
    aux_data_arr = []

    for classifier in classifiers_names:
        for key, value in prob_dict.items():
            if value["classifier_name"] == classifier:
                aux_data_arr.append(value)
        group_data_dict[classifier] = aux_data_arr
        aux_data_arr = []

    pprint.pprint(group_data_dict)

    return group_data_dict

@router.get("/probabilities/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):

    prob_list = get_probabilities(oid,session_factory = request.app.state.psql_session)
    taxonomy_list = get_taxonomies(session_factory = request.app.state.psql_session)

    taxonomy_dict, prob_dict = prob_filter(prob_list, taxonomy_list)

    group_prob_dict = group_data_by_classifier(prob_dict)
    filtered_taxonomy = filter_classifier_name_taxonomy(taxonomy_dict)

    return templates.TemplateResponse(
      name='prob.html.jinja',
      context={'request': request,
               'prob_dict': prob_dict,
               'taxonomy_dict': filtered_taxonomy,
               'group_prob_dict': group_prob_dict,
               },
  )


@router.get("/probabilities2/{oid}", response_class=HTMLResponse)
async def object_probability_app(
    request: Request,
    oid: str,
):

    prob_list = get_probabilities(oid,session_factory = request.app.state.psql_session)
    taxonomy_list = get_taxonomies(session_factory = request.app.state.psql_session)

    taxonomy_dict, prob_dict = prob_filter(prob_list, taxonomy_list)

    return templates.TemplateResponse(
      name='probabilitiesCard.html.jinja',
      context={'request': request,
               'prob_dict': prob_dict,
               'taxonomy_dict': taxonomy_dict,
               },
  )