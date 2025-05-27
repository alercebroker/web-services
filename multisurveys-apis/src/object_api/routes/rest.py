import traceback
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Query
from ..models.filters import Filters, Consearch, SearchParams
from ..models.pagination import Pagination, Order
from ..services.object_services import get_object_list

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
    class_name: str,
    oid: Annotated[list[str] | None, Query()] = None,
    classifier: str | None = None,
    classifier_version: str | None = None,
    ranking: int | None = Query(default=1),
    ndet: Annotated[list[int] | None, Query()] = None,
    probability: float | None = Query(default=0),
    firstmjd: Annotated[list[float] | None, Query()] = None,
    lastmjd: float | None = None,
    dec: float | None = None,
    ra: float | None = None,
    radius: float | None = None,
    page: int | None = 1,
    page_size: int | None = 10,
    count: bool | None = False,
    order_by: str | None = Query(default="probability"),
    order_mode: str | None = Query(default="DESC"),
    ):
    
    try:
        session = request.app.state.psql_session

        filters = Filters(oid, classifier, classifier_version, class_name, ranking, ndet, probability, firstmjd, lastmjd)

        conesearch = Consearch(dec, ra, radius)

        pagination = Pagination(page, page_size, count)

        order = Order(order_by, order_mode)

        search_params = SearchParams(filters, conesearch, pagination, order)

        object_list = get_object_list(
            session_factory=session,
            search_params = search_params
        )


        return object_list
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")
    

# @router.get("/get_object/{id}")
# def get_object(
#     request: Request, 
#     id: str
#     ):
#     try:
#         session = request.app.state.psql_session
#         object_info = get_unique_object_rest(id, session)

#         return JSONResponse(object_info)
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"An error occurred")
    

# @router.get("/limit_values")
# def get_object(
#     request: Request, 
#     ):
#     try:
#         session = request.app.state.psql_session
#         response = get_limit_values_rest(session)

#         return JSONResponse(response)
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"An error occurred")