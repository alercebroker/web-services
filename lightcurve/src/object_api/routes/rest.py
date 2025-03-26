from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from ..services.object_service_rest import (get_object_list)
import pprint

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
    filter_args: dict, 
    conesearch_args: dict, 
    pagination_args: dict,
    order_args: dict
    ):
    
    try:
        session = request.app.state.psql_session
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
        print({str(e)})
        raise HTTPException(status_code=500, detail=f"An error occurred")