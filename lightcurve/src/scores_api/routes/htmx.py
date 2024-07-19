import re
import os
from typing import Annotated
from fastapi import Query
import json

from core.services.object import get_scores, get_scores_distribution, get_taxonomies
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/scores_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "OBJECT_API_URL", "http://localhost:8000"
)

@router.get("/scores/{oid}", response_class=HTMLResponse)
async def scores_app(
    request: Request,
    oid: str,
):
    
    #scores = get_scores(oid="prueba", session_factory = request.app.state.psql_session)
    #nota el detector name se puede sacar 1 por cada detector de score
    #distributions = get_scores_distribution(detector_name="anomaly_detector", session_factory = request.app.state.psql_session)
    
    scores = get_scores(oid, session_factory = request.app.state.psql_session)
    print("SCORES:-------\n", scores)
    distributions = get_scores_distribution("anomaly_detector", session_factory = request.app.state.psql_session)
    print("DISTRIBUTIONS:---------\n", distributions)
    taxonomies = get_taxonomies(session_factory = request.app.state.psql_session)
    # una tabla con 
    # category | score | decil (el mas chico de los que sean mayores) numero (valor del percentil) | 
    table_rows = []

    def str_separator(word):

        if word == 'saturation':
            return float(100)
        else:
            return float(word.split('_')[1])

    for dic in range(len(scores)):

        current_category = scores[dic].__dict__['category_name']
        current_score = float(scores[dic].__dict__['score'])
    
        flag = 0

        for dist in range(len(distributions)):

            if distributions[dist].__dict__['category_name'] == current_category:
                if flag == 0:
                    if current_score < float(distributions[dist].__dict__['distribution_value']):
                        flag = 1
                        def_value = distributions[dist].__dict__['distribution_value']
                        def_index = dist
        
            if flag == 1:
                break
        
        if flag == 1:
            percentil = str_separator(distributions[def_index].__dict__['distribution_name'])
        else: 
            percentil = 0
            def_value = 0 

        table_rows.append({'category': current_category, 'score': current_score, 'percentil': percentil, 'percentil_cut': def_value})
        

    print("---------------\n", table_rows)
    # armar el input para la tabla scores

    return templates.TemplateResponse(
      name='scoresCards.html.jinja',
      context={'request': request,
               'table_rows': table_rows
               },
  )