import json
import requests

def get_tns(ra, dec):
    data = send_request_tns(ra, dec)
    check_data(data)
    tns_link = add_tns_link(data)

    return data, tns_link
    
    
def send_request_tns(ra, dec):

    headersSend = {
    "accept": "application/json",
    "cache-control": "no-cache",
    "content-type": "application/json"
    }

    payload = {"ra": ra, "dec": dec}
    payload_dump = json.dumps(payload)

    url = "https://api.staging.alerce.online/v2/tns_api/search"

    response = requests.post(url, data=payload_dump, headers=headersSend)
    
    response.raise_for_status()

    return response.json()

        
def check_data(data):

    for index, values in data.items():

        if values["redshift"] == None or values["redshift"] == "empty":
            values["redshift"] = '-'
        
        if values["name"] == None or values["name"] == "empty":
            values["name"] = '-'
        
        if values["type"] == None or values["type"] == "empty":
            values ["type"] = '-'
    
    return data


def add_tns_link(data):
    for index, values in data.items():
        if values["name"] != '-':
            return 'https://www.wis-tns.org/object/' + values["name"]
        else:
            return 'https://www.wis-tns.org/'

