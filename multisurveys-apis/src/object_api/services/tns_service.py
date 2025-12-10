import json
import requests


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

        data = check_data(data)
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
