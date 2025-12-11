import os
import traceback
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..services.object_services import get_tidy_classifiers
from ..models.filters import Consearch, Filters, SearchParams
from ..models.pagination import Order, PaginationArgs
from ..services.object_services import get_objects_list
from ..services.validations import (
    ndets_validation,
    order_mode_validation,
    consearch_validation,
    oids_format_validation,
    oid_lenght_validation,
    date_validation,
    probability_validation,
)
from ..services.tns_service import get_tns
from ..services.idmapper.idmapper import encode_ids
from ..services.jinja_tools import truncate_float
from core.exceptions import ObjectNotFound
from object_api.services.object_services import (
    get_object_by_id,
)
from ..services.parsers import _parse_oids_string_to_array

router = APIRouter()

templates = Jinja2Templates(directory="src/object_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8000")

templates.env.filters["truncate"] = truncate_float


@router.get("/htmx/object_information", response_class=HTMLResponse)
async def object_info_app(request: Request, oid: str, survey_id: str):
    try:
        object_data = get_object_by_id(oid, survey_id, session_ms=request.app.state.psql_session)

        other_archives = [
            "DESI Legacy Survey DR11",
            "NED",
            "PanSTARRS",
            "SDSS DR19",
            "SIMBAD",
            "TNS",
            "Vizier",
            "VSX",
        ]

    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="basic_information/basicInformationPreview.html.jinja",
        context={
            "request": request,
            "object": str(object_data["oid"]),
            "survey_id": survey_id,
            "detections": object_data["n_det"],
            "nonDetections": object_data["n_non_det"],
            "discoveryDateMJD": object_data["firstmjd"],
            "lastDetectionMJD": object_data["lastmjd"],
            "ra": object_data["meanra"],
            "dec": object_data["meandec"],
            "measurement_id": object_data["sid"],
            "otherArchives": other_archives,
        },
    )


@router.get("/htmx/tns/", response_class=HTMLResponse)
async def tns_info(request: Request, ra: float, dec: float):
    try:
        tns_data, tns_link = get_tns(ra, dec)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="basic_information/oldTnsInformation.html.jinja",
        context={
            "request": request,
            "tns_data": tns_data,
            "tns_link": tns_link,
            "object_name": tns_data["object_name"],
            "object_type": tns_data["object_type"],
            "redshift": tns_data["object_data"]["redshift"],
            "discoverer": tns_data["object_data"]["discoverer"],
            "discovery_data_source": tns_data["object_data"]["discovery_data_source"],
        },
    )


@router.get("/htmx/search_objects/", response_class=HTMLResponse)
async def objects_form(request: Request):
    try:
        session = request.app.state.psql_session
        classifiers = get_tidy_classifiers(session)

        return templates.TemplateResponse(
            name="form.html.jinja",
            context={"request": request, "classifiers": classifiers},
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/htmx/classes_select", response_class=HTMLResponse)
async def select_classes_classifier(request: Request, classifier_classes: list[str] = Query(...)):
    try:
        classes = classifier_classes

        return templates.TemplateResponse(
            name="dependent_select.html.jinja",
            context={"request": request, "classes": classes},
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/htmx/list_objects", response_class=HTMLResponse)
def objects_table(
    request: Request,
    class_name: str | None = None,
    oid: str | None = None,
    survey: str | None = None,
    classifier: str | None = None,
    ranking: int | None = Query(default=1),
    n_det: Annotated[list[int] | None, Query()] = None,
    n_det_min: int | None = None,
    n_det_max: int | None = None,
    probability: float | None = None,
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
    try:
        if survey is not None:
            session = request.app.state.psql_session
            oid = _parse_oids_string_to_array(oid)


            if n_det_min is not None or n_det_max is not None:
                n_det = []
                if n_det_min is not None:
                    n_det.append(n_det_min)
                if n_det_max is not None:
                    n_det.append(n_det_max)
                n_det = n_det if len(n_det) > 0 else None

            ndets_validation(n_det)
            order_mode_validation(order_mode)
            consearch_validation(ra, dec, radius)
            oids_format_validation(oid, survey)
            oid_lenght_validation(oid)
            probability_validation(probability, classifier, class_name)
            date_validation(firstmjd)


            if oid is not None:
                oid = encode_ids(survey, oid)

            filters = Filters(
                oids=oid,
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

            object_list = get_objects_list(session_ms=session, search_params=search_params)

        else:
            object_list = {
                "next": False,
                "has_next": False,
                "prev": False,
                "has_prev": False,
                "items": [],
                "info_message": "Results will appear here",
            }

        return templates.TemplateResponse(
            name="objects_table.html.jinja",
            context={
                "request": request,
                "objects_list": object_list,
                "next": object_list["next"],
                "has_next": object_list["has_next"],
                "prev": object_list["prev"],
                "has_prev": object_list["has_prev"],
                "actual_order_by": order_by,
                "actual_order_mode": order_mode,
            },
        )
    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/htmx/side_objects", response_class=HTMLResponse)
def sidebar(
    request: Request,
    survey: str | None = None,
    oid: str | None = None,
    selected_oid: str | None = None,
    classifier: str | None = None,
    class_name: str | None = None,
    ranking: int | None = Query(default=1),
    n_det: Annotated[list[int] | None, Query()] = None,
    n_det_min: int | None = None,
    n_det_max: int | None = None,
    probability: float | None = None,
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
    try:
        if survey is not None:
            session = request.app.state.psql_session
            oid = _parse_oids_string_to_array(oid)

            n_det = []
            if n_det_min is not None:
                n_det.append(n_det_min)
            if n_det_max is not None:
                n_det.append(n_det_max)
            n_det = n_det if len(n_det) > 0 else None

            ndets_validation(n_det)
            order_mode_validation(order_mode)
            consearch_validation(ra, dec, radius)
            oids_format_validation(oid, survey)
            oid_lenght_validation(oid)
            probability_validation(probability, classifier, class_name)
            date_validation(firstmjd)

            if oid is not None:
                oid = encode_ids(survey, oid)

            filters = Filters(
                oids=oid,
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

            object_list = get_objects_list(session_ms=session, search_params=search_params)
        else:
            object_list = {
                "next": False,
                "has_next": False,
                "prev": False,
                "has_prev": False,
                "items": [],
                "info_message": "Results will appear here",
            }

        return templates.TemplateResponse(
            name="sidebar.html.jinja",
            context={
                "request": request,
                "objects_list": object_list,
                "next": object_list["next"],
                "has_next": object_list["has_next"],
                "prev": object_list["prev"],
                "has_prev": object_list["has_prev"],
                "actual_order_by": order_by,
                "actual_order_mode": order_mode,
                "selected_oid": selected_oid,
            },
        )
    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
