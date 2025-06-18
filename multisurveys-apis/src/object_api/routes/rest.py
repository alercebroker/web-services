import traceback
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from ..models.filters import Consearch, Filters, SearchParams
from ..models.pagination import Order, OrderMode, PaginationArgs
from ..services.object_services import get_objects_list, get_object_by_id
from ..services.validations import ndets_validation

router = APIRouter()


@router.get("/")
def root():
    return "this is the object module"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/list_objects")
def list_objects(
    request: Request,
    class_name: str | None = None,
    oid: Annotated[list[str] | None, Query()] = None,
    classifier: str | None = Query(default="lc_classifier"),
    classifier_version: str | None = Query(
        default="hierarchical_random_forest_1.1.0"
    ),
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
    order_mode: OrderMode = OrderMode.desc,
):
    try:
        session = request.app.state.psql_session
        
        ndets_validation(ndet)

        filters = Filters(
            oids=oid,
            classifier=classifier,
            classifier_version=classifier_version,
            class_name=class_name,
            ranking=ranking,
            ndet=ndet,
            probability=probability,
            firstmjd=firstmjd,
            lastmjd=lastmjd,
        )

        conesearch = Consearch(dec=dec, ra=ra, radius=radius)

        pagination = PaginationArgs(page=page, page_size=page_size, count=count)

        order = Order(order_by=order_by, order_mode=order_mode)

        search_params = SearchParams(
            filter_args=filters,
            conesearch_args=conesearch,
            pagination_args=pagination,
            order_args=order,
        )

        object_list = get_objects_list(
            session_ms=session, search_params=search_params
        )

        return object_list
    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/object")
def get_object(request: Request, id: str, survey_id: str):
    try:
        session = request.app.state.psql_session

        response = get_object_by_id(session, id, survey_id)

        return response
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")

