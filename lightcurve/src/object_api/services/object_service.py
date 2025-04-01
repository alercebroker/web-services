import json
import requests
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from core.exceptions import  ObjectNotFound
from core.repository.queries.object import query_psql_object
from core.repository.queries.non_detections import _query_count_non_detections_sql
from core.repository.queries.detections import _query_first_det_candid_sql

from ..models.object import ObjectReduced as ObjectModel

def get_object(
    oid: str, 
    session_factory: Callable[..., AbstractContextManager[Session]]
) -> ObjectModel:
    try:

        first = query_psql_object(oid=oid, session_factory=session_factory)

        return ObjectModel(**first.__dict__)
    except Exception:
        raise
    

def get_count_ndet(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> int:
    
    try:
        count = _query_count_non_detections_sql(oid=oid, session_factory=session_factory)

        return count
    except Exception:
        raise

def get_first_det_candid(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> str:
    try:
        first = _query_first_det_candid_sql(oid=oid, session_factory=session_factory)

        detection = first[0].__dict__
        
        if detection is None:
            raise ObjectNotFound(oid)
        
        return detection["candid"]
    except ObjectNotFound:
        raise


def add_tns_link(data):
    
    if data["object_name"] != '-': 
       return 'https://www.wis-tns.org/object/' + data["object_name"]
    else:
        return 'https://www.wis-tns.org/'

def check_data(data):
    
    if "object_data" in data and len(data["object_data"]) > 25:
        if data["object_data"]["redshift"] == None:
            data["object_data"]["redshift"] = '-'
    else:
        raise ValueError("Data does not meet the required condition")

    if "object_name" in data:
        if data["object_name"] == None:
            data["object_name"] = '-'
    else:
        raise ValueError("Data does not meet the required condition")
    
    if "object_type" in data:
        if data["object_type"] == None:
            data["object_type"] = '-'
    else:
        raise ValueError("Data does not meet the required condition")
    
    return data

def error_data():
    tns_data = {
        "object_data": {
            "discoverer": "-",
            "discovery_data_source": { "group_name": "-"},
            "redshift": "-",
        },
        "object_name": "-",
        "object_type": "-"
    }
    tns_link = 'https://www.wis-tns.org/'

    return tns_data, tns_link


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
        tns_link = add_tns_link(data)

        return data, tns_link
        
    except requests.exceptions.RequestException as error:
        print(f"Error: {error}")
        tns = error_data()
        return tns
    
    except ValueError as e:
        print(f"Error: {e}")

        tns = error_data()
        return tns