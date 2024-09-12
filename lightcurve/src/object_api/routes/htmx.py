import json
import os

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
        "typeInput": "",
        "name": "",
        "redshift": "",
        "tnsLink": "https://www.wis-tns.org/"
    }
    
    if data == True:
        informationDict["typeInput"] = "-"
        informationDict["name"] = "-"
        informationDict["redshift"] = "-"
    elif isinstance(data, dict) and data:
        if len(data["object_data"]) > 25:
            informationDict["typeInput"] = data["object_type"]
            informationDict["name"] = data["object_name"]
            informationDict["redshift"] = data["object_data"]["redshift"]
        else:
            informationDict["typeInput"] = "-"
            informationDict["name"] = "-"
            informationDict["redshift"] = "-"
    else:
        informationDict["typeInput"] = "Unexpected response"
        informationDict["name"] = "Unexpected response"
        informationDict["redshift"] = "Unexpected response"
        
    return informationDict


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

        text = response.text

        if "Error message" in text:
            print(response)
            print(response.text)
            raise requests.exceptions.RequestException("Error found in response: " + text)
        
        try:
            data = response.json()
        except ValueError:
            raise requests.exceptions.RequestException("Error found in response: " + text)

        tns_data = last_information(data)

        return tns_data
        
    except requests.exceptions.RequestException as error:
        tns_data = last_information(True)

        return tns_data

@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(request: Request, oid: str):
    try:
        object_data = get_object(oid, request.app.state.psql_session)
        candid = get_first_det_candid(oid, request.app.state.psql_session)
        count_ndet = get_count_ndet(oid, request.app.state.psql_session)
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
        },
    )

@router.get("/tns/{oid}", response_class=HTMLResponse)
async def tns_info(request: Request, oid: str):
    try:
        object_data = get_object(oid, request.app.state.psql_session)
        tns_data = get_tns(object_data.meanra, object_data.meandec)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Object ID not found")

    return templates.TemplateResponse(
        name="tnsInformation.html.jinja",
        context={"request": request}|tns_data
    )
