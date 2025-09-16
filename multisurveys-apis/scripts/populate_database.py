import argparse
import os
import random
from typing import cast
import sys

import yaml
from db_plugins.db.sql import models
from faker import Faker
from faker.providers import BaseProvider

from core.config.connection import ApiDatabase
from core.idmapper import idmapper


class ALeRCEProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)
        self._measurement_ids = set()
        self._ztf_oids = set()

    def ra(self) -> float:
        return random.uniform(0, 360)

    def dec(self) -> float:
        return random.uniform(-90, 90)

    def sigma(self) -> float:
        return random.uniform(0, 1)

    def mjd(self) -> float:
        return random.uniform(59000, 61000)

    def deltamjd(self) -> float:
        return random.uniform(0, 365)

    def close_coord(self, coord: float, delta=0.5) -> float:
        return coord + random.uniform(-delta, delta)

    def band(self, sid: int) -> int:
        if sid == 1:
            return self.random_int(1, 3)
        if sid == 2:
            return self.random_int(0, 5)
        else:
            raise ValueError("Invalid survey id")

    def magnitude(self) -> float:
        return random.uniform(15, 25)

    def version(self) -> str:
        return "v0.1.0"

    def measurement_id(self):
        tries = 0
        while True:
            val = self.random_int(0, sys.maxsize)
            if val not in self._measurement_ids:
                self._measurement_ids.add(val)
                return val
            tries += 1
            if tries > 1000:
                raise ValueError(f"Could not find a new unique int after {tries} tries. ")

    def ztf_oid(self):
        tries = 0
        while True:
            val = "".join(self.random_letters(7))
            if val not in self._ztf_oids:
                self._ztf_oids.add(val)
                return idmapper.catalog_oid_to_masterid(
                    "ZTF",
                    f"ZTF{self.random_int(18, 25)}{val}",
                ).item()
            tries += 1
            if tries > 1000:
                raise ValueError("Could not find a new unique ZTF OID after 1000 tries.")


def generate_object(faker: Faker):
    sid = faker.random_int(1, 2)
    oid: int
    if sid == 1:
        oid = faker.ztf_oid()
    else:
        oid = faker.unique.random_int()
    return models.Object(
        oid=oid,
        tid=sid,
        sid=sid,
        meanra=faker.ra(),
        meandec=faker.dec(),
        sigmara=faker.sigma(),
        sigmadec=faker.sigma(),
        firstmjd=faker.mjd(),
        lastmjd=faker.mjd(),
        deltamjd=faker.deltamjd(),
        n_det=faker.random_int(1, 50),
        n_forced=faker.random_int(1, 50),
        n_non_det=faker.random_int(1, 50) if sid == 1 else 0,
        corrected=faker.boolean(),
        stellar=faker.boolean(),
    )


def generate_detection(faker: Faker, obj: models.Object):
    return models.Detection(
        oid=obj.oid,
        sid=obj.sid,
        measurement_id=faker.measurement_id(),
        mjd=faker.mjd(),
        ra=faker.close_coord(obj.meanra),
        dec=faker.close_coord(obj.meandec),
        band=faker.band(obj.sid),
    )


def generate_ztf_detection(faker: Faker, det: models.Detection):
    return models.ZtfDetection(
        oid=det.oid,
        sid=det.sid,
        measurement_id=det.measurement_id,
        pid=faker.random_int(1, 3),
        diffmaglim=faker.pyfloat(min_value=15, max_value=25),
        isdiffpos=faker.random_int(0, 1),
        nid=faker.random_int(1, 3),
        magpsf=faker.magnitude(),
        sigmapsf=faker.sigma(),
        magap=faker.magnitude(),
        sigmagap=faker.sigma(),
        distnr=faker.pyfloat(min_value=0, max_value=10),
        rb=faker.pyfloat(min_value=0, max_value=1),
        rbversion=faker.version(),
        drb=faker.pyfloat(min_value=0, max_value=1),
        drbversion=faker.version(),
        magapbig=faker.magnitude(),
        sigmagapbig=faker.sigma(),
        rfid=faker.random_int(1, 3),
        magpsf_corr=faker.magnitude(),
        sigmapsf_corr=faker.sigma(),
        sigmapsf_corr_ext=faker.sigma(),
        corrected=faker.boolean(),
        dubious=faker.boolean(),
        parent_candid=None,
        has_stamp=True,
    )


def generate_lsst_detection(faker: Faker, det: models.Detection):
    return models.LsstDetection(
        oid=det.oid,
        sid=det.sid,
        measurement_id=det.measurement_id,
        psfFlux=faker.pyfloat(min_value=50, max_value=300),
        psfFluxErr=faker.pyfloat(min_value=0, max_value=2),
        scienceFlux=faker.pyfloat(min_value=50, max_value=300),
        scienceFluxErr=faker.pyfloat(min_value=0, max_value=2),
        visit=faker.random_int(),
        detector=faker.random_int(),
        x=faker.pyfloat(min_value=0, max_value=64),
        y=faker.pyfloat(min_value=0, max_value=64),
        timeProcessedMjdTai=faker.pyfloat(min_value=0, max_value=60),
    )


def generate_ztf_non_detection(faker: Faker, obj: models.Object):
    return models.ZtfNonDetection(
        oid=obj.oid,
        sid=obj.sid,
        band=faker.band(obj.sid),
        mjd=faker.mjd(),
        diffmaglim=faker.pyfloat(min_value=18, max_value=25),
    )


def generate_forced_photometry(faker: Faker, obj: models.Object):
    return models.ForcedPhotometry(
        oid=obj.oid,
        sid=obj.sid,
        measurement_id=faker.measurement_id(),
        mjd=faker.mjd(),
        ra=faker.close_coord(obj.meanra),
        dec=faker.close_coord(obj.meandec),
        band=faker.band(obj.sid),
    )


def generate_ztf_forced_photometry(faker: Faker, det: models.Detection):
    return models.ZtfForcedPhotometry(
        oid=det.oid,
        sid=det.sid,
        measurement_id=det.measurement_id,
        mag=faker.magnitude(),
        e_mag=faker.sigma(),
        mag_corr=faker.magnitude(),
        e_mag_corr=faker.sigma(),
        e_mag_corr_ext=faker.sigma(),
        isdiffpos=faker.random_int(0, 1),
        corrected=faker.boolean(),
        dubious=faker.boolean(),
        has_stamp=True,
        field=faker.random_int(1, 3),
        rcid=faker.random_int(1, 3),
        rfid=faker.random_int(1, 3),
        sciinpseeing=faker.pyfloat(min_value=0, max_value=1),
        scibckgnd=faker.pyfloat(min_value=0, max_value=1),
        scisigpix=faker.pyfloat(min_value=0, max_value=1),
        magzpsci=faker.magnitude(),
        magzpsciunc=faker.magnitude(),
        magzpscirms=faker.magnitude(),
        clrcoeff=faker.pyfloat(min_value=0, max_value=1),
        clrcounc=faker.pyfloat(min_value=0, max_value=1),
        exptime=faker.pyfloat(min_value=0, max_value=1),
        adpctdif1=faker.pyfloat(min_value=0, max_value=1),
        adpctdif2=faker.pyfloat(min_value=0, max_value=1),
        diffmaglim=faker.pyfloat(min_value=0, max_value=1),
        programid=faker.random_int(1, 3),
        procstatus=faker.pyfloat(min_value=0, max_value=1),
        distnr=faker.pyfloat(min_value=0, max_value=1),
        ranr=faker.ra(),
        decnr=faker.dec(),
        magnr=faker.magnitude(),
        sigmagnr=faker.sigma(),
        chinr=faker.pyfloat(min_value=0, max_value=1),
        sharpnr=faker.pyfloat(min_value=0, max_value=1),
    )


def generate_lsst_forced_photometry(faker: Faker, fphot: models.ForcedPhotometry):
    return models.LsstForcedPhotometry(
        oid=fphot.oid,
        sid=fphot.sid,
        measurement_id=fphot.measurement_id,
        psfFlux=faker.pyfloat(min_value=50, max_value=300),
        psfFluxErr=faker.pyfloat(min_value=0, max_value=2),
        scienceFlux=faker.pyfloat(min_value=50, max_value=300),
        scienceFluxErr=faker.pyfloat(min_value=0, max_value=2),
        visit=faker.random_int(1, 3),
        detector=faker.random_int(1, 3),
        timeProcessedMjdTai=faker.pyfloat(min_value=0, max_value=1),
    )


def config_from_yaml():
    """
    Read the config from a yaml file and return a dict.
    The file is expected to be in the root of the app.
    """
    import pathlib

    root_folder = pathlib.Path(__file__).parent.parent.resolve()
    config_file_name = "config.yaml"
    config_file = os.path.join(root_folder, config_file_name)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config


def export_db_secrets(config: dict):
    os.environ["PSQL_USER"] = config["psql_user"]
    os.environ["PSQL_PASSWORD"] = config["psql_password"]
    os.environ["PSQL_DATABASE"] = config["psql_database"]
    os.environ["PSQL_HOST"] = config["psql_host"]
    os.environ["PSQL_PORT"] = str(config["psql_port"])
    os.environ["SCHEMA"] = config["psql_schema"]


def generate_lightcurve(faker: Faker, obj: models.Object):
    detections = []
    survey_detections = []
    non_detections = []
    forced_photometry = []
    survey_forced_photometry = []
    for _ in range(cast(int, obj.n_det)):
        detections.append(generate_detection(faker, obj))
        if cast(int, obj.sid) == 1:  # ZTF
            survey_detections.append(generate_ztf_detection(faker, detections[-1]))
        else:  # lsst
            survey_detections.append(generate_lsst_detection(faker, detections[-1]))

    for _ in range(cast(int, obj.n_non_det)):
        non_detections.append(generate_ztf_non_detection(faker, obj))

    for _ in range(cast(int, obj.n_forced)):
        forced_photometry.append(generate_forced_photometry(faker, obj))
        if cast(int, obj.sid) == 1:  # ZTF
            survey_forced_photometry.append(generate_ztf_forced_photometry(faker, forced_photometry[-1]))
        else:  # lsst
            survey_forced_photometry.append(generate_lsst_forced_photometry(faker, forced_photometry[-1]))

    return (
        detections,
        survey_detections,
        non_detections,
        forced_photometry,
        survey_forced_photometry,
    )


def main():
    parser = argparse.ArgumentParser(description="Populate database")
    parser.add_argument("service", type=str, help="the name of the service")
    parser.add_argument("nobjects", type=int, help="number of objects")
    args = parser.parse_args()
    config = config_from_yaml().get("services").get(args.service).get("db_config")
    export_db_secrets(config)
    db = ApiDatabase()
    fake = Faker()
    fake.add_provider(ALeRCEProvider)

    with db.session() as session:
        for _ in range(args.nobjects):
            obj = generate_object(fake)
            session.add(obj)
            session.commit()
            (
                detections,
                survey_detections,
                non_detections,
                forced_photometry,
                survey_forced_photometry,
            ) = generate_lightcurve(fake, obj)

            session.add_all(detections)
            session.add_all(forced_photometry)
            session.add_all(non_detections)
            session.commit()

            session.add_all(survey_detections)
            session.add_all(survey_forced_photometry)
