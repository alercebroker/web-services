import json
import os
import shelve
import zipfile
import astropy.units as u
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
from astropy.coordinates import SkyCoord

DATA_PATH = os.path.abspath(os.environ["DATA_PATH"])

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

last_updated: None | datetime = None
df_tns = pd.DataFrame()


def get_object_tns(ra: float, dec: float):
    ut_timezone = timezone(-timedelta(hours=6))
    now = datetime.now(ut_timezone)

    if not last_updated or now - last_updated > timedelta(hours=1):
        update_parquet()

    closest_object_coordinates = get_closest_object(ra, dec, df_tns)

    object_result = query_df_object(df_tns, closest_object_coordinates)

    object_result = replace_NaN_values(object_result)

    object_dict = object_result.to_dict(orient="index")


    return json.dumps(object_dict, allow_nan=True)


def update_parquet():
    global last_updated, df_tns
    parquet_path = os.path.join(DATA_PATH, "tns.parquet")
    df_tns = pd.read_parquet(parquet_path)

    shelve_path = os.path.join(DATA_PATH, "info")
    with shelve.open(shelve_path) as info:
        last_updated = info["last_archive"]


def get_closest_object(ra, dec, df):
    ra_numpy_array = df.ra.to_numpy()
    dec_numpy_array = df.declination.to_numpy()

    parquet_catalog_coordinates = SkyCoord(
        ra=ra_numpy_array * u.deg, dec=dec_numpy_array * u.deg, frame="icrs", unit="deg"
    )
    incoming_coordinates = SkyCoord(
        ra=ra * u.deg, dec=dec * u.deg, frame="icrs", unit="deg"
    )

    idx, _, _ = incoming_coordinates.match_to_catalog_3d(parquet_catalog_coordinates)

    closest_object_coordinates = parquet_catalog_coordinates[idx.item(0)]


    return closest_object_coordinates


def query_df_object(df, object):
    query = f"ra == {object.ra.value} and declination == {object.dec.value}"
    result = df.query(query)
    result.index = ['object_data']

    return result


def replace_NaN_values(df):
    df = df.replace(np.nan, "empty")

    return df


def download_tns_base_csv():
    print(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            "tns_public_objects.csv.zip",
        ),
    )

    response = requests.post(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            "tns_public_objects.csv.zip",
        ),
        headers=TNS_CSV_HEADER,
        data=TNS_CSV_DATA,
    )

    csv_path = os.path.join(DATA_PATH, "tns_public_objects.csv.zip")
    with open(csv_path, "wb") as file:
        file.write(response.content)
    print("Saved csv to:", csv_path)


def download_tns_hourly_csv(t: datetime):
    t_str = t.strftime("%H")
    print(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            f"tns_public_objects_{t_str}.csv.zip",
        ),
    )

    response = requests.post(
        urljoin(
            TNS_WIS_PUBLIC_OBJECTS_URL,
            f"tns_public_objects_{t_str}.csv.zip",
        ),
        headers=TNS_CSV_HEADER,
        data=TNS_CSV_DATA,
    )

    csv_path = os.path.join(DATA_PATH, f"tns_public_objects_{t_str}.csv.zip")
    with open(csv_path, "wb") as file:
        file.write(response.content)
    print("Saved csv to:", csv_path)


def build_tns_parquet():
    ut_timezone = timezone(-timedelta(hours=6))
    now = datetime.now(ut_timezone)

    shelve_path = os.path.join(DATA_PATH, "info")
    info = shelve.open(shelve_path)

    if "last_archive" in info:
        print(info["last_archive"], now)
    else:
        print("No last_archive", now)

    if "last_archive" not in info or now - info["last_archive"] > timedelta(days=1):
        print("Downloading base CSV")
        download_tns_base_csv()

        print("Building base parquet")
        csv_path = os.path.join(DATA_PATH, "tns_public_objects.csv.zip")
        zip_file = zipfile.ZipFile(csv_path)
        df = pd.read_csv(zip_file.open("tns_public_objects.csv"), skiprows=1)
        parquet_path = os.path.join(DATA_PATH, "tns.parquet")
        df.to_parquet(parquet_path)

        info["last_archive"] = now.replace(hour=0, minute=0, second=0, microsecond=0)
        print("Updated last archive", info["last_archive"])

    print("Loading tns parquet")
    parquet_path = os.path.join(DATA_PATH, "tns.parquet")
    df_tns = pd.read_parquet(parquet_path)

    updated = False
    t: datetime = info["last_archive"] + timedelta(hours=1)
    while t < now:
        t += timedelta(hours=1)
        t_str = t.strftime("%H")

        print("Downloading update for hour", t_str)
        download_tns_hourly_csv(t)

        print("Loading update for hour", t_str)
        csv_path = os.path.join(DATA_PATH, f"tns_public_objects_{t_str}.csv.zip")
        zip_file = zipfile.ZipFile(csv_path)

        try:
            df_update = pd.read_csv(
                zip_file.open(f"tns_public_objects_{t_str}.csv"), skiprows=1
            )
        except pd.errors.EmptyDataError:
            print("No data to update on CSV")
            continue

        print("Updating for hour", t_str)
        df_tns.update(df_update)
        updated = True

    if updated:
        print("Saving updated parquet to", parquet_path)
        df_tns.to_parquet(parquet_path)

        info["last_archive"] = now
        print("Updated last archive", info["last_archive"])
    else:
        print("Nothing to update")
