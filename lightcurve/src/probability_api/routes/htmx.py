import os
from fastapi import FastAPI, Request, Query

from ..services.probability_service import (
    get_probabilities,
    get_taxonomies,
    taxonomy_data,
    group_data_by_classifier_dict,
    filter_data_by_higher_version,
    classifiers_options)
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(
    directory="src/probability_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8004"
)


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
    
    class_options = classifiers_options(group_prob_by_version)


    return templates.TemplateResponse(
      name='prob.html.jinja',
      context={'request': request,
               'taxonomy_dict': taxonomy_dict,
               'group_prob_dict': group_prob_by_version,
               'class_dict': class_options
               },
  )
