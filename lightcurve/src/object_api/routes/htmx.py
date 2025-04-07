import traceback
import os
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import Field
from fastapi import Query
from core.exceptions import ObjectNotFound
from ..models.info import filters_model, conesearch_model, pagination_model, order_model
from ..services.object_service import(
    get_object, 
    get_count_ndet, 
    get_first_det_candid,
    get_tns,
    get_classifiers,
    get_classifier_classes
    )
from ..services.object_service_rest import (
    get_object_list, 
)

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8001"
)


@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(request: Request, oid: str):
    try:
        object_data = get_object(oid, request.app.state.psql_session)
        candid = get_first_det_candid(oid, request.app.state.psql_session)
        count_ndet = get_count_ndet(oid, request.app.state.psql_session)

        other_archives = ['DESI Legacy Survey DR10', 'NED', 'PanSTARRS', 'SDSS DR18', 'SIMBAD', 'TNS', 'Vizier', 'VSX']

    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")


    return templates.TemplateResponse(
        name="basicInformationPreview.html.jinja",
        context={
            "request": request,
            "object": object_data.oid,
            "corrected": "Yes" if object_data.corrected else "No",
            "stellar": "Yes" if object_data.stellar else "No",
            "detections": object_data.ndet,
            "nonDetections": count_ndet,
            "discoveryDateMJD": object_data.firstmjd,
            "lastDetectionMJD": object_data.lastmjd,
            "ra": object_data.meanra,
            "dec": object_data.meandec,
            "candid": str(candid),
            "otherArchives": other_archives,
        },
    )


@router.get("/list_object")
def list_object(
    request: Request,
    class_name: str,
    oid: str | None = None,
    classifier: str | None = None,
    classifier_version: str | None = None,
    ranking: int | None = 1,
    ndet: Annotated[list[str] | None, Query()] = None,
    probability: float | None = None,
    firstmjd: float | None = None,
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

        filters = filters_model(
            oid = oid,
            classifier = classifier,
            classifier_version = classifier_version,
            class_name = class_name,
            ranking = ranking,
            ndet = ndet,
            probability = probability,
            firstmjd = firstmjd,
            lastmjd = lastmjd,
        )

        conesearch = conesearch_model(
            dec = dec,
            ra = ra,
            radius = radius
        )

        pagination = pagination_model(
            page = page,
            page_size = page_size,
            count = count
        )

        order = order_model(
            order_by = order_by,
            order_mode = order_mode
        )

        default_classifier = "lc_classifier"
        default_version =  "hierarchical_random_forest_1.1.0"
        default_ranking =  1

        object_list = get_object_list(
            session_factory=session,
            filter_args=filters,
            conesearch_args=conesearch,
            pagination_args=pagination,
            order_args=order,
            default_classifier=default_classifier,
            default_version=default_version,
            default_ranking=default_ranking
        )


        return JSONResponse(object_list)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")

@router.get("/tns/", response_class=HTMLResponse)
async def tns_info(request: Request, ra: float, dec:float):
    try:
        tns_data, tns_link = get_tns(ra, dec)

    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="tnsInformation.html.jinja",
        context={
            "request": request,
            "tns_data": tns_data,
            "tns_link": tns_link,
            "object_name": tns_data["object_name"],
            "object_type": tns_data["object_type"],
            "redshift": tns_data["object_data"]["redshift"],
            "discoverer": tns_data["object_data"]["discoverer"],
            "discovery_data_source": tns_data["object_data"]["discovery_data_source"]
        }
    )

@router.get("/form/", response_class=HTMLResponse)
async def tns_info(request: Request):

    try:
        session = request.app.state.psql_session
        classifiers = get_classifiers(session)

        return templates.TemplateResponse(
        name="form.html.jinja",
        context={
            "request": request,
            "classifiers": classifiers
        }
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")
    


@router.get("/select/", response_class=HTMLResponse)
async def tns_info(
    request: Request,
    classifier_name: str,
    classifier_version: str
    ):

    try:
        session = request.app.state.psql_session
        classes = get_classifier_classes(session, classifier_name, classifier_version)

        return templates.TemplateResponse(
        name="dependentSelect.html.jinja",
        context={
            "request": request,
            "classes": classes
        }
    )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")