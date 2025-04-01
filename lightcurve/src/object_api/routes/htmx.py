
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.exceptions import ObjectNotFound
from ..services.object_service import(
    get_object, 
    get_count_ndet, 
    get_first_det_candid,
    get_tns
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