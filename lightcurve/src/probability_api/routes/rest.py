import re
import os
from typing import Annotated
from fastapi import Query
import json

from core.services.object import get_probabilities,get_taxonomies
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)

def prob_filter(prob_list, taxonomy_list):

    prob_dict = {}
    taxonomy_dict  = {}

    for n in range(len(taxonomy_list)):
        taxonomy_dict[f'tax_{n+1}'] = taxonomy_list[n].__dict__

    for k in range(len(prob_list)):
        prob_dict[f'prob_{k+1}'] = prob_list[k].__dict__

    return taxonomy_dict, prob_dict

@router.get("/probabilities/{oid}", response_class=HTMLResponse)
async def object_crossmatch_app(
    request: Request,
    oid: str
):
    prob_list = get_probabilities(oid,session_factory = request.app.state.psql_session)
    taxonomy_list = get_taxonomies(session_factory = request.app.state.psql_session)

    taxonomy_dict, prob_dict = prob_filter(prob_list, taxonomy_list)

    return {'request': request,
               'prob_dict': prob_dict,
               'taxonomy_dict': taxonomy_dict
            },