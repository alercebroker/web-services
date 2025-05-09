import os
import shelve
import zipfile
import json
import astropy.units as u
from astropy.coordinates import SkyCoord
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import pandas as pd
import requests

TNS_DATA_PATH = os.path.abspath(os.environ["TNS_DATA_PATH"])

TNS_CSV_HEADER = {
    "user-agent": f'tns_marker{{"tns_id": {os.environ["TNS_BOT_ID"]}, "type": "bot", "name": "{os.environ["TNS_BOT_NAME"]}"}}',
    "content-type": "application/x-www-form-urlencoded",
}

TNS_CSV_DATA = {
    "api_key": os.environ["TNS_BOT_API_KEY"],
}

TNS_WIS_PUBLIC_OBJECTS_URL = urljoin(
    os.environ["TNS_WIS_BASE_URL"], "/system/files/tns_public_objects/"
)


def get_object_tns(ra: float, dec: float):
    
    csv_path = os.path.join(TNS_DATA_PATH, "tns.parquet")
    df = pd.read_parquet(csv_path)

    closest_object_coordinates = get_closest_object(ra, dec, df)

    object_result = query_df_object(df, closest_object_coordinates)

    object_dict = object_result.to_dict(orient="index")

    print(object_dict)

    return json.dumps(object_dict, allow_nan=True)


def get_closest_object(ra, dec, df):

    ra_numpy_array = df.ra.to_numpy()
    dec_numpy_array = df.declination.to_numpy()

    parquet_catalog_coordinates = SkyCoord(ra=ra_numpy_array*u.deg, dec=dec_numpy_array*u.deg, frame="icrs", unit="deg") 
    incoming_coordinates = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame="icrs", unit="deg")

    idx, d2d, d3d = incoming_coordinates.match_to_catalog_3d(parquet_catalog_coordinates)

    closest_object_coordinates = parquet_catalog_coordinates[idx.item(0)]

    return closest_object_coordinates

def query_df_object(df, object):
    query = f"ra == {object.ra.value} and declination == {object.dec.value}"
    result = df.query(query)

    return result

def download_tns_base_csv():
    ut_timezone = timezone(-timedelta(hours=6))
    now = datetime.now(ut_timezone)

    print(TNS_CSV_HEADER, TNS_CSV_DATA)

    shelve_path = os.path.join(TNS_DATA_PATH, "info")
    info = shelve.open(shelve_path)

    if "last_archive" in info:
        print(info["last_archive"], now)
    else:
        print(None, now)

    print(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            "tns_public_objects.csv.zip",
        ),
    )

    # Today archive already downloaded
    if "last_archive" in info and info["last_archive"].date() == now.date():
        print("Already downloaded CSV")
        return

    response = requests.post(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            "tns_public_objects.csv.zip",
        ),
        headers=TNS_CSV_HEADER,
        data=TNS_CSV_DATA,
    )

    csv_path = os.path.join(TNS_DATA_PATH, "tns_public_objects.csv.zip")
    with open(csv_path, "wb") as file:
        file.write(response.content)

    print("Saved csv to:", csv_path)

    info["last_archive"] = now
    info.close()

    print("Updated info shelve")


def build_tns_parquet():
    print("Start CSV download")
    download_tns_base_csv()
    print("Finish CSV download")

    print("Start load CSV to DF")
    csv_path = os.path.join(TNS_DATA_PATH, "tns_public_objects.csv.zip")
    zip_file = zipfile.ZipFile(csv_path)
    df = pd.read_csv(zip_file.open("tns_public_objects.csv"), skiprows=1)
    print("Finish Load CSV to DF")

    parquet_path = os.path.join(TNS_DATA_PATH, "tns.parquet")
    df.to_parquet(parquet_path)
    print("Finish building TNS parquet")


# def get_tns_hourly_csv(time: datetime | None):
#     if time is None:
#         ut_timezone = timezone(-timedelta(hours=6))
#         time = datetime.now(ut_timezone)
#     time_str = time.strftime("%H")
#
#     response = requests.post(
#         urljoin(
#             TNS_WIS_PUBLIC_OBJECTS_URL,
#             f"tns_public_objects_{time_str}.csv.zip",
#         ),
#         headers=TNS_CSV_HEADER,
#         data=TNS_CSV_DATA,
#     )
