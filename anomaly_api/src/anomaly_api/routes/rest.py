import os
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from anomaly_api.database.alerts_queries import (
    ProbabilityFilter,
    get_object_list,
    get_objects_by_oid,
)
from anomaly_api.database.score_queries import (
    get_objects_by_score,
    get_scores_by_oid,
    get_scores_list,
)

router = APIRouter()

router = APIRouter()

templates = Jinja2Templates(
    directory="./src/anomaly_api/templates", autoescape=True, auto_reload=True
)

templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")


def filterArr(element, data):
    # splitElements = [item.strip() for item in elements.split(",")]
    # print(splitElements)
    # print(element)
    if element == "":
        return data
    else:
        filtered_data = [item for item in data if item["oid"] == element]
        return filtered_data


@router.get("/")
def root():
    return "this is the anomaly module"


@router.get("/grafico", response_class=HTMLResponse)
def grafico(request: Request):
    return templates.TemplateResponse(
        name="anomaly_template.html.jinja",
        context={
            "request": request,
        },
    )


@router.get("/tabla", response_class=HTMLResponse)
def tabla(
    request: Request,
    objectId: Annotated[list[str] | None, Query()] = None,
    min_dets: int = None,
    max_dets: int = None,
    classifier_name: str = None,
    class_name: str = None,
    min_probability: float = None,
    max_probability: float = None,
    score_query: Annotated[list[str] | None, Query()] = None,
    page: int = 1,
    per_page: int = 10,
):
    """
    score_quert=(category_name, min_value | None, max_value | None)
    """

    print(f"Object Ids : {objectId} \n")
    print(f" min dets = {min_dets}, max_det = {max_dets}\n")
    print(
        f"Probability filter\n classifier_name = {classifier_name} class name = {class_name}"
    )
    print(f"min proba = {min_probability}   max probability = {max_probability}")

    prob_filter = None
    prob_class = None
    if not (
        classifier_name == None
        or class_name == None
        or (min_probability == None and max_probability == None)
    ):
        print("Con filtro de probability")
        prob_filter = ProbabilityFilter(
            classifier_name, class_name, min_probability, max_probability
        )
        prob_class = class_name
    else:
        print("Sin filtro de probability")

    score_query_list = None
    if not score_query == None:
        print(score_query)
        score_query_list = []
        for sq in score_query:
            score_stmt_args = sq[1:-1].split(",")
            if len(score_stmt_args) == 3:
                score_query_list.append(
                    {
                        "category": score_stmt_args[0],
                        "min_score": None
                        if score_stmt_args[1] == "None"
                        else score_stmt_args[1],
                        "max_score": None
                        if score_stmt_args[2] == "None"
                        else score_stmt_args[2],
                    }
                )
            else:
                print("Bad score query")

        print(f"Score querys\n {score_query_list}")

    # ---------------------------------------------------------------
    # idea?
    # separar en 3 branches
    # solos oids
    # filtros ndets y scores
    # filtros prob, ndet y scores

    # if prob_filter == None and score_query_list == None:
    #    print("solo oids")

    # if prob_filter == None and not score_query_list == None:
    #     print("query con ndet y score")

    # if not (prob_filter == None and score_query_list == None):
    #     print("query con prob")
    # ---------------------------------------------------------------

    # pedir objectos por oid, pedir scores por oids, merge

    scores_result = get_scores_list(objectId, score_query_list)
    scores_dicts = [s_r.model_dump() for s_r in scores_result]
    scores_df = pd.DataFrame(scores_dicts)
    scores_df.set_index("oid")
    print(f"----\n scores data\n{scores_df}")

    filtered_oids = scores_df["oid"].to_list()
    print(f"-----\n filtered oifs : {filtered_oids}")

    objects_result = get_object_list(filtered_oids, min_dets, max_dets, prob_filter)
    objects_dicts = [o_r.model_dump() for o_r in objects_result]
    objects_df = pd.DataFrame(objects_dicts)
    objects_df.set_index("oid")
    print(f"-------\nalerts_data\n{objects_df}")

    merged_df = pd.merge(scores_df, objects_df, on="oid")
    print(f"----\nmerged data\n{merged_df.to_dict('records')}")

    filterData = merged_df.to_dict("records")

    start = (page - 1) * per_page
    end = start + per_page
    total_pages = len(filterData) / per_page
    paginated_data = filterData[start:end]

    return templates.TemplateResponse(
        name="table_template.html.jinja",
        context={
            "request": request,
            "data": paginated_data,
            "prob_class": prob_class,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total": len(filterData),
        },
    )


@router.get("/detalles", response_class=HTMLResponse)
def detalles(request: Request):
    return templates.TemplateResponse(
        name="details_template.html.jinja",
        context={
            "request": request,
        },
    )
