import json
import os

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pprint import pprint 
from core.exceptions import ObjectNotFound
from core.services.object import (
    get_count_ndet,
    get_first_det_candid,
    get_object,
)

router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8001"
)


def last_information(data):
    informationDict = {
        "typeInput": "-",
        "name": "-",
        "redshift": "-",
        "discoverer": "-",
        "discovery_data_source": "-",
        "tnsLink": "https://www.wis-tns.org/"
    }

    if(data == "Error"):
        return informationDict
    
    if(len(data["object_data"]) > 25):
        informationDict["typeInput"] = data["object_type"]
        informationDict["name"] = data["object_name"]
        informationDict["redshift"] = data["object_data"]["redshift"]
        informationDict["discoverer"] = data["object_data"]["discoverer"]
        informationDict["discovery_data_source"] = data["object_data"]["discovery_data_source"]

    return informationDict

def check_data(data):
    
    if "object_data" in data:
        pass
    else:
        raise ValueError("Data does not meet the required condition")

    if "object_name" in data:
        pass
    else:
        raise ValueError("Data does not meet the required condition")
    
    if "object_type" in data:
        pass
    else:
        raise ValueError("Data does not meet the required condition")
    
    if(len(data["object_data"]) > 25):
        return data
    else:
        raise ValueError("Data does not meet the required condition")
    

def get_tns(ra, dec):
    try:
        headersSend = {
        "accept": "application/json",
        "cache-control": "no-cache",
        "content-type": "application/json"
        }
        payload = {"ra": ra, "dec": dec}
        payload_dump = json.dumps(payload)

        response = requests.post("https://tns.alerce.online/search", data=payload_dump, headers=headersSend)

        data = response.json()

        check_data(data)

        return data
        
    except requests.exceptions.RequestException as error:
        print(f"Error: {error}")

        tns_data = {
        "object_data": {
            "discoverer": "-",
            "discovery_data_source": { "group_name": "-"},
            "redshift": "-",
        },
        "object_name": "-",
        "object_type": "-"
        }

        return tns_data
    
    except ValueError as e:
        print(f"Error: {e}")

        tns_data = {
        "object_data": {
            "discoverer": "-",
            "discovery_data_source": { "group_name": "-"},
            "redshift": "-",
        },
        "object_name": "-",
        "object_type": "-"
        }

        return tns_data

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
            "candid": candid,
            "otherArchives": other_archives,
        },
    )

@router.get("/tns/", response_class=HTMLResponse)
async def tns_info(request: Request, ra: float, dec:float):
    try:
        tns_data = get_tns(ra, dec)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="tnsInformation.html.jinja",
        context={
            "request": request,
            "tns_data": tns_data,
            "object_name": tns_data["object_name"],
            "object_type": tns_data["object_type"],
            "redshift": tns_data["object_data"]["redshift"],
            "discoverer": tns_data["object_data"]["discoverer"],
            "discovery_data_source": tns_data["object_data"]["discovery_data_source"]
        }
    )