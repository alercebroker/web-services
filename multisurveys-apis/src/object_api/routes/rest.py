from typing import Annotated

from fastapi import APIRouter, Query, Request

from core.idmapper.idmapper import decode_ids

from ..models.filters import Consearch, Filters, SearchParams
from ..models.pagination import Order, PaginationArgs
from ..services.object_services import get_object_by_id, get_objects_list
from ..services.validations import (
    ndets_validation,
    order_mode_validation,
    pagination_validation,
    survey_validation,
)
from ..services.parameters_parser import parse_oids_to_int

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
    survey: str | None = None,
    classifier: str | None = None,
    ranking: int | None = Query(default=1),
    n_det: Annotated[list[int] | None, Query()] = None,
    probability: float | None = Query(default=0),
    firstmjd: Annotated[list[float] | None, Query()] = None,
    lastmjd: Annotated[list[float] | None, Query()] = None,
    dec: float | None = None,
    ra: float | None = None,
    radius: float | None = None,
    page: int | None = 1,
    page_size: int | None = 10,
    count: bool | None = False,
    order_by: str | None = Query(default="probability"),
    order_mode: str | None = Query(default="DESC"),
):
    session = request.app.state.psql_session

    survey_validation(survey)
    ndets_validation(n_det)
    order_mode_validation(order_mode)
    pagination_validation(page, page_size)

    filters = Filters(
        oids=parse_oids_to_int(oid, survey),
        survey=survey,
        classifier=classifier,
        class_name=class_name,
        ranking=ranking,
        n_det=n_det,
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

    return get_objects_list(session_ms=session, search_params=search_params)


@router.get("/object")
def get_object(request: Request, oid: str, survey_id: str, return_survey_extra: bool = False):
    session = request.app.state.psql_session
    survey_id = survey_id.lower()

    response = get_object_by_id(
        session_ms=session,
        oid=oid,
        survey_id=survey_id,
        return_survey_extra=return_survey_extra,
    )
    if survey_id == "ztf":
        decode_ids([response])
    return response
