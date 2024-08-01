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
    
    # Si scores = vacio, retornar nada (no hay data)
    scores = get_scores(oid, session_factory = request.app.state.psql_session)
    distributions = get_scores_distribution(session_factory = request.app.state.psql_session)
    taxonomies = get_taxonomies(session_factory = request.app.state.psql_session)

    scores_data = {}

    if len(scores) != 0:
        for taxonomie in taxonomies:
            taxonomie_dict = taxonomie.__dict__
            if "detector" in taxonomie_dict["classifier_name"].split("_"):
                scores_data[taxonomie_dict["classifier_name"]] = {
                    "categories": {
                        x: {} for x in taxonomie_dict["classes"]
                    }
                }

        for score in scores:
            score_dict = score.__dict__
            if score_dict["detector_name"] in scores_data.keys():
                scores_data[score_dict["detector_name"]]["categories"][score_dict["category_name"]]["score"] = score_dict["score"]
                scores_data[score_dict["detector_name"]]["categories"][score_dict["category_name"]]["percentil"] = 0
                scores_data[score_dict["detector_name"]]["categories"][score_dict["category_name"]]["percentil_cut"] = 0
                scores_data[score_dict["detector_name"]]["categories"][score_dict["category_name"]]["graph_data"] = []

        for distribution in distributions:
            distribution_dict = distribution.__dict__
            if distribution_dict["detector_name"] in scores_data.keys():
                if "percentil" in distribution_dict["distribution_name"].split("_") or "saturation" == distribution_dict["distribution_name"]:
                    scores_data[distribution_dict["detector_name"]]["categories"][distribution_dict["category_name"]]["graph_data"].append({
                        "label": distribution_dict["distribution_name"], "value": distribution_dict["distribution_value"]
                    })
                    if (distribution_dict["distribution_value"] <= scores_data[distribution_dict["detector_name"]]["categories"][distribution_dict["category_name"]]["score"] 
                    and
                    distribution_dict["distribution_value"] > scores_data[distribution_dict["detector_name"]]["categories"][distribution_dict["category_name"]]["percentil_cut"]):
                        scores_data[distribution_dict["detector_name"]]["categories"][distribution_dict["category_name"]]["percentil"] = distribution_dict["distribution_name"]
                        scores_data[distribution_dict["detector_name"]]["categories"][distribution_dict["category_name"]]["percentil_cut"] = distribution_dict["distribution_value"]

    import pprint
    print("DEBUG-----\n")
    pprint.pprint(scores_data)

    return templates.TemplateResponse(
      name='scoresCards.html.jinja',
      context={'request': request,
               'scores_data': scores_data #Si scores = 0, entonces scores = {}
               },
  )