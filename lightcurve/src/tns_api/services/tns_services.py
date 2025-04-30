import requests
import json
import pprint

def get_object_tns(ra: float, dec: float):


    headers_send = {
        "accept": "application/json",
        "cache-control": "no-cache",
        "content-type": "application/json"
    }

    payload = {"ra": ra, "dec": dec}

    response = requests.post('https://tns.alerce.online/search', data=payload, headers=headers_send)

    if response.status_code == 200:
        return payload
    else:
        raise Exception(f"Request failed with status {response.status_code}")
