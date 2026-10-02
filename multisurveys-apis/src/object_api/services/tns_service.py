import json
import requests

# 3 s to connect, 10 s to wait for data. TNS answers in about 1 s (measured from a crossmatch pod, 01/10/2026).
# A timeout is a RequestException, so it shows the "-" card like any other TNS failure.
TNS_TIMEOUT = (3, 10)


def get_tns(ra, dec):
    try:
        headersSend = {"accept": "application/json", "cache-control": "no-cache", "content-type": "application/json"}
        payload = {"ra": ra, "dec": dec}
        payload_dump = json.dumps(payload)

        response = requests.post(
            "https://tns.alerce.online/search", data=payload_dump, headers=headersSend, timeout=TNS_TIMEOUT
        )

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
    if data["object_name"] != "-":
        return "https://www.wis-tns.org/object/" + data["object_name"]
    else:
        return "https://www.wis-tns.org/"


def check_data(data):
    if "object_data" in data and len(data["object_data"]) > 25:
        if data["object_data"]["redshift"] is None:
            data["object_data"]["redshift"] = "-"
    else:
        raise ValueError("Data does not meet the required condition")

    if "object_name" in data:
        if data["object_name"] is None:
            data["object_name"] = "-"
    else:
        raise ValueError("Data does not meet the required condition")

    if "object_type" in data:
        if data["object_type"] is None:
            data["object_type"] = "-"
    else:
        raise ValueError("Data does not meet the required condition")

    return data


def error_data():
    tns_data = {
        "object_data": {
            "discoverer": "-",
            "discovery_data_source": {"group_name": "-"},
            "redshift": "-",
        },
        "object_name": "-",
        "object_type": "-",
    }
    tns_link = "https://www.wis-tns.org/"

    return tns_data, tns_link
