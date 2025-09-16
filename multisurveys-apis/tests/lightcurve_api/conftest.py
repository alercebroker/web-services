import os
from typing import Tuple

import pytest
from db_plugins.db.sql._connection import PsqlDatabase
from db_plugins.db.sql.models import (
    Detection,
    LsstDetection,
    Object,
    ZtfDetection,
    ZtfNonDetection,
    ForcedPhotometry,
    ZtfForcedPhotometry,
    LsstForcedPhotometry,
)
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from core.config.connection import ApiDatabase
from core.idmapper import idmapper
from core.repository.queries.create_q3c_index import create_q3c_idx
from lightcurve_api.api import app


@pytest.fixture(scope="session")
def db_setup():
    with DockerImage(
        path=".",
        dockerfile_path="Dockerfile-psql",
        tag="base-psql:latest",
        clean_up=False,
    ) as image:
        with (
            DockerContainer(str(image))
            .with_env("POSTGRES_DB", "multistream")
            .with_env("POSTGRES_USER", "alerce")
            .with_env("POSTGRES_PASSWORD", "alerce")
            .with_exposed_ports("5432/tcp") as container
        ):
            wait_for_logs(
                container,
                "ready to accept connections",
                timeout=10,
            )

            host = container.get_container_host_ip()
            os.environ["PSQL_USER"] = "alerce"
            os.environ["PSQL_PASSWORD"] = "alerce"
            os.environ["PSQL_DATABASE"] = "multistream"
            os.environ["PSQL_HOST"] = host
            os.environ["PSQL_PORT"] = str(container.get_exposed_port("5432/tcp"))
            db = ApiDatabase()
            db.create_db()
            create_q3c_idx(db)
            yield db
            db.drop_db()


@pytest.fixture(scope="session")
def client(db_setup):
    _ = db_setup  # this line silences pyright unused db_setup
    return TestClient(app)


@pytest.fixture(scope="function")
def populate_database(faker: Faker, db_setup: PsqlDatabase):
    def _populate(n=100):
        # start with a known object
        objects = [
            Object(
                oid=idmapper.catalog_oid_to_masterid("ZTF", "ZTF20aaelulu").item(),
                tid=1,
                sid=1,
                meanra=faker.latitude(),
                meandec=faker.longitude(),
                firstmjd=faker.random_int(min=59000, max=61000),
                lastmjd=faker.random_int(min=59000, max=61000),
                deltamjd=faker.random_int(min=0, max=365),
                n_det=faker.random_int(min=0, max=100),
                n_forced=faker.random_int(min=0, max=100),
                n_non_det=faker.random_int(min=0, max=100),
                corrected=faker.boolean(),
            ),
            Object(
                oid=1234,
                tid=2,
                sid=2,
                meanra=faker.latitude(),
                meandec=faker.longitude(),
                firstmjd=faker.random_int(min=59000, max=61000),
                lastmjd=faker.random_int(min=59000, max=61000),
                deltamjd=faker.random_int(min=0, max=365),
                n_det=faker.random_int(min=0, max=100),
                n_forced=faker.random_int(min=0, max=100),
                n_non_det=faker.random_int(min=0, max=100),
                corrected=faker.boolean(),
            ),
        ]
        ztf_detections = []
        lsst_detections = []
        detections = []
        non_detections = []
        forced_photometry = []
        ztf_forced_photometry = []
        lsst_forced_photometry = []

        # add n more objects with random values
        for _ in range(n):
            obj = _generate_ztf_object(faker)
            objects.append(obj)
            for i in range(n):
                detection, ztf_detection = _generate_ztf_detection(faker, obj.oid, i)
                detections.append(detection)
                ztf_detections.append(ztf_detection)
                non_detections.append(_generate_non_detection(faker, obj.oid, i))
                fphot, ztf_fphot = _generate_ztf_forced_photometry(faker, obj.oid, i)
                ztf_forced_photometry.append(ztf_fphot)
                forced_photometry.append(fphot)
        for _ in range(n):
            obj = _generate_lsst_object(faker)
            objects.append(obj)
            for i in range(n):
                detection, lsst_detection = _generate_lsst_detection(faker, obj.oid, i)
                detections.append(detection)
                lsst_detections.append(lsst_detection)
                fphot, lsst_fphot = _generate_lsst_forced_photometry(faker, obj.oid, i)
                lsst_forced_photometry.append(lsst_fphot)
                forced_photometry.append(fphot)
        session: Session
        with db_setup.session() as session:
            session.add_all(objects)
            session.commit()
            session.add_all(ztf_detections)
            session.add_all(lsst_detections)
            session.add_all(detections)
            session.add_all(non_detections)
            session.add_all(ztf_forced_photometry)
            session.add_all(lsst_forced_photometry)
            session.add_all(forced_photometry)
            session.commit()

    yield _populate
    with db_setup.session() as session:
        session.execute(text("DELETE FROM detection"))
        session.execute(text("DELETE FROM ztf_detection"))
        session.execute(text("DELETE FROM lsst_detection"))
        session.execute(text("DELETE FROM forced_photometry"))
        session.execute(text("DELETE FROM ztf_forced_photometry"))
        session.execute(text("DELETE FROM lsst_forced_photometry"))
        session.execute(text("DELETE FROM ztf_non_detection"))
        session.execute(text("DELETE FROM object"))
        session.commit()


def _generate_ztf_object(faker: Faker) -> Object:
    return Object(
        oid=idmapper.catalog_oid_to_masterid(
            "ZTF",
            f"ZTF{faker.year()[2:]}{''.join(faker.unique.random_letters(7))}",
        ).item(),
        tid=1,
        sid=1,
        meanra=faker.latitude(),
        meandec=faker.longitude(),
        firstmjd=faker.random_int(min=59000, max=61000),
        lastmjd=faker.random_int(min=59000, max=61000),
        deltamjd=faker.random_int(min=0, max=365),
        n_det=faker.random_int(min=0, max=100),
        n_forced=faker.random_int(min=0, max=100),
        n_non_det=faker.random_int(min=0, max=100),
        corrected=faker.boolean(),
    )


def _generate_ztf_detection(faker: Faker, oid, idx) -> Tuple[Detection, ZtfDetection]:
    return Detection(
        oid=oid,
        sid=1,
        measurement_id=idx,
        mjd=faker.random_int(min=59000, max=61000),
        ra=faker.latitude(),
        dec=faker.longitude(),
        band=1,
    ), ZtfDetection(
        oid=oid,
        sid=1,
        measurement_id=idx,
        magpsf=faker.pyfloat(min_value=15, max_value=25),
        sigmapsf=faker.pyfloat(min_value=0, max_value=10),
    )


def _generate_lsst_object(faker: Faker) -> Object:
    return Object(
        oid=faker.unique.random_int(),
        tid=2,
        sid=2,
        meanra=faker.latitude(),
        meandec=faker.longitude(),
        firstmjd=faker.random_int(min=59000, max=61000),
        lastmjd=faker.random_int(min=59000, max=61000),
        deltamjd=faker.random_int(min=0, max=365),
        n_det=faker.random_int(min=0, max=100),
        n_forced=faker.random_int(min=0, max=100),
        n_non_det=faker.random_int(min=0, max=100),
        corrected=faker.boolean(),
    )


def _generate_lsst_detection(faker: Faker, oid, idx) -> Tuple[Detection, LsstDetection]:
    return Detection(
        oid=oid,
        sid=2,
        measurement_id=idx,
        mjd=faker.random_int(min=59000, max=61000),
        ra=faker.latitude(),
        dec=faker.longitude(),
        band=1,
    ), LsstDetection(
        oid=oid,
        sid=2,
        measurement_id=idx,
        diaSourceId=idx + 1,
        visit=idx + 1,
        detector=idx + 1,
        x=1,
        y=1,
        timeProcessedMjdTai=1,
    )


def _generate_non_detection(faker: Faker, oid, idx):
    return ZtfNonDetection(
        oid=oid,
        sid=1,
        band=1,
        mjd=faker.unique.pyfloat(min_value=59000, max_value=61000),
        diffmaglim=faker.pyfloat(min_value=0, max_value=10),
    )


def _generate_ztf_forced_photometry(faker: Faker, oid, idx):
    return ForcedPhotometry(
        oid=oid,
        sid=1,
        measurement_id=idx,
        mjd=faker.random_int(min=59000, max=61000),
        ra=faker.latitude(),
        dec=faker.longitude(),
        band=1,
    ), ZtfForcedPhotometry(
        oid=oid,
        sid=1,
        measurement_id=idx,
        mag=faker.pyfloat(min_value=15, max_value=25),
        e_mag=faker.pyfloat(min_value=0, max_value=10),
        isdiffpos=faker.random_int(),
        corrected=faker.boolean(),
        dubious=faker.boolean(),
        has_stamp=faker.boolean(),
        field=faker.random_int(),
        rcid=faker.random_int(),
        rfid=faker.random_int(),
        sciinpseeing=faker.pyfloat(min_value=0, max_value=10),
        scibckgnd=faker.pyfloat(min_value=0, max_value=10),
        scisigpix=faker.pyfloat(min_value=0, max_value=10),
        magzpsci=faker.pyfloat(min_value=0, max_value=10),
        magzpsciunc=faker.pyfloat(min_value=0, max_value=10),
        magzpscirms=faker.pyfloat(min_value=0, max_value=10),
        clrcoeff=faker.pyfloat(min_value=0, max_value=10),
        clrcounc=faker.pyfloat(min_value=0, max_value=10),
        exptime=faker.pyfloat(min_value=0, max_value=10),
        adpctdif1=faker.pyfloat(min_value=0, max_value=10),
        adpctdif2=faker.pyfloat(min_value=0, max_value=10),
        diffmaglim=faker.pyfloat(min_value=0, max_value=10),
        programid=faker.random_int(),
        procstatus=faker.random_int(),
        distnr=faker.pyfloat(min_value=0, max_value=10),
        ranr=faker.pyfloat(min_value=0, max_value=10),
        decnr=faker.pyfloat(min_value=0, max_value=10),
        magnr=faker.pyfloat(min_value=0, max_value=10),
        sigmagnr=faker.pyfloat(min_value=0, max_value=10),
        chinr=faker.pyfloat(min_value=0, max_value=10),
        sharpnr=faker.pyfloat(min_value=0, max_value=10),
    )


def _generate_lsst_forced_photometry(faker: Faker, oid, idx):
    return ForcedPhotometry(
        oid=oid,
        sid=2,
        measurement_id=idx,
        mjd=faker.random_int(min=59000, max=61000),
        ra=faker.latitude(),
        dec=faker.longitude(),
        band=1,
    ), LsstForcedPhotometry(
        oid=oid,
        sid=2,
        measurement_id=idx,
        visit=faker.random_int(),
        detector=faker.random_int(),
        timeProcessedMjdTai=faker.random_int(),
    )
