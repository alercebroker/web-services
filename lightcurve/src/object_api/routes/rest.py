import traceback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from ..models.info import filters_model, conesearch_model, pagination_model, order_model
from ..services.object_service_rest import (get_object_list, get_unique_object_rest, get_limit_values_rest)

router = APIRouter()

@router.get("/")
def root():
    return "this is the object module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/list_object")
def list_object(
    request: Request,
    filter_args: filters_model, 
    conesearch_args: conesearch_model, 
    pagination_args: pagination_model,
    order_args: order_model
    ):
    
    try:
        session = request.app.state.psql_session

        filter_args = filter_args.dict()
        conesearch_args = conesearch_args.dict()
        pagination_args = pagination_args.dict()
        order_args = order_args.dict()

        default_classifier = "lc_classifier"
        default_version =  "hierarchical_random_forest_1.1.0"
        default_ranking =  1

        object_list = get_object_list(
            session_factory=session,
            filter_args=filter_args,
            conesearch_args=conesearch_args,
            pagination_args=pagination_args,
            order_args=order_args,
            default_classifier=default_classifier,
            default_version=default_version,
            default_ranking=default_ranking
        )


        return JSONResponse(object_list)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")
    

@router.get("/get_object/{id}")
def get_object(
    request: Request, 
    id: str
    ):
    try:
        session = request.app.state.psql_session
        object_info = get_unique_object_rest(id, session)

        return JSONResponse(object_info)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")
    

@router.get("/limit_values")
def get_object(
    request: Request, 
    ):
    try:
        session = request.app.state.psql_session
        response = get_limit_values_rest(session)

        return JSONResponse(response)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")