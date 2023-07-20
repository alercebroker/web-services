from db_plugins.db.mongo.connection import MongoDatabaseCreator
from db_plugins.db.sql.connection import SQLDatabaseCreator
from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
import datetime
import signal
import time


def psql_ready():
    try:
        conn = SQLDatabaseCreator().create_database()
        settings = {
            "ENGINE": "postgresql",
            "HOST": "localhost",
            "DB_NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "PORT": 5432,
        }
        conn.connect(settings)
        conn.create_db()
        return True
    except Exception as e:
        print(e)
        return False


def mongo_ready():
    try:
        mongo_db = MongoDatabaseCreator().create_database()
        settings = {
            "HOST": "localhost",
            "DATABASE": "database",
            "USERNAME": "mongo",
            "PASSWORD": "mongo",
            "PORT": 27017,
        }
        mongo_db.connect(settings)
        mongo_db.client.close()
        return True
    except Exception:
        return False


def wait_for_service(timeout: int, pause: float, callback, service):
    """Wait until postgres service is ready.

    Params
    ------------
    timeout : int
        Seconds to wait for postgres service
    pause : float
        Seconds to wait between checks
    callback : callable
        Callable that performs the check.
        Must return True if service is available.
        Must return False if service is not available.
    """

    def timeout_handler(signum, frame):
        raise Exception(f"Timed out waiting for {service} service")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    while True:
        if callback():
            signal.alarm(0)
            break
        time.sleep(pause)


def insert_psql_data():
    creator = SQLDatabaseCreator()
    sql_db = creator.create_database()
    settings = {
        "ENGINE": "postgresql",
        "HOST": "localhost",
        "DB_NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "PORT": 5432,
    }
    sql_db.connect(settings)
    sql_db.create_db()
    model = psql_models.Object(
        oid="ZTF1",
        ndet=1,
        lastmjd=1.0,
        meanra=1.0,
        meandec=1.0,
        sigmara=1.0,
        sigmadec=1.0,
        deltajd=1.0,
        firstmjd=1.0,
    )
    model2 = psql_models.Object(
        oid="ZTF2",
        ndet=1,
        lastmjd=1.0,
        meanra=1.0,
        meandec=1.0,
        sigmara=1.0,
        sigmadec=1.0,
        deltajd=1.0,
        firstmjd=1.0,
    )
    step = psql_models.Step(
        step_id="test_step",
        name="preprocess",
        version="1",
        comments="asd",
        date=datetime.datetime.now(),
    )
    model.detections.append(
        psql_models.Detection(
            candid=123,
            mjd=1,
            fid=1,
            pid=1,
            isdiffpos=1,
            ra=1,
            dec=1,
            rb=1,
            magpsf=1,
            sigmapsf=1,
            corrected=True,
            dubious=True,
            has_stamp=True,
            step_id_corr=step.step_id,
        )
    )
    model2.detections.append(
        psql_models.Detection(
            candid=456,
            mjd=1,
            fid=1,
            pid=1,
            isdiffpos=1,
            ra=1,
            dec=1,
            rb=1,
            magpsf=1,
            sigmapsf=1,
            corrected=True,
            dubious=True,
            has_stamp=True,
            step_id_corr=step.step_id,
        )
    )
    model.non_detections.append(
        psql_models.NonDetection(mjd=1, fid=1, diffmaglim=1)
    )
    sql_db.session.add(model)
    sql_db.session.add(model2)
    sql_db.session.commit()
    sql_db.session.close()


def insert_mongo_data():
    creator = MongoDatabaseCreator()
    mongo_db = creator.create_database()
    settings = {
        "HOST": "localhost",
        "DATABASE": "database",
        "USERNAME": "mongo",
        "PASSWORD": "mongo",
        "PORT": 27017,
    }
    mongo_db.connect(settings)
    mongo_db.create_db()
    mongo_object = mongo_models.Object(
        aid="AID1",
        oid=["ATLAS1"],
        lastmjd="lastmjd",
        firstmjd="firstmjd",
        meanra=100.0,
        meandec=50.0,
        ndet="ndet",
        tid=["ATLAS"],
        sid=["ATLAS"],
        corrected=False,
        stellar=False,
        sigmara=0.1,
        sigmadec=0.1,
    )
    mongo_object_2 = mongo_models.Object(
        aid="AID2",
        oid=["ATLAS2", "ZTF1"],
        lastmjd="lastmjd",
        firstmjd="firstmjd",
        meanra=100.0,
        meandec=50.0,
        ndet="ndet",
        tid=["ATLAS", "ZTF"],
        sid=["ATLAS", "ZTF"],
        corrected=False,
        stellar=False,
        sigmara=0.1,
        sigmadec=0.1,
    )
    mongo_detections = mongo_models.Detection(
        tid="ATLAS01",
        sid="ATLAS",
        aid="AID1",
        oid="ATLAS1",
        candid="candid1",
        mjd=1,
        fid=1,
        ra=1,
        dec=1,
        rb=1,
        mag=1,
        mag_corr=1,
        e_mag=1,
        e_mag_corr=1,
        e_mag_corr_ext=1,
        rfid=1,
        e_ra=1,
        e_dec=1,
        isdiffpos=1,
        magpsf_corr=1,
        sigmapsf_corr=1,
        sigmapsf_corr_ext=1,
        corrected=True,
        dubious=True,
        parent_candid=1234,
        has_stamp=True,
        step_id_corr="step_id_corr",
        rbversion="rbversion",
    )
    mongo_detections_2 = mongo_models.Detection(
        tid="ATLAS02",
        sid="ATLAS",
        aid="AID2",
        oid="ZTF1",
        candid="candid2",
        mjd=1,
        fid=1,
        ra=1,
        dec=1,
        rb=1,
        mag=1,
        mag_corr=1,
        e_mag=1,
        e_mag_corr=1,
        e_mag_corr_ext=1,
        rfid=1,
        e_ra=1,
        e_dec=1,
        isdiffpos=1,
        magpsf_corr=1,
        sigmapsf_corr=1,
        sigmapsf_corr_ext=1,
        corrected=True,
        dubious=True,
        parent_candid=float("nan"),
        has_stamp=True,
        step_id_corr="step_id_corr",
        rbversion="rbversion",
    )
    mongo_non_detections = mongo_models.NonDetection(
        candid="candid1",
        sid="ZTF",
        aid="AID1",
        oid="ZTF1",
        tid="ZTF",
        mjd=1,
        diffmaglim=1,
        fid=1,
    )
    mongo_db.query().get_or_create(mongo_object, model=mongo_models.Object)
    mongo_db.query().get_or_create(mongo_object_2, model=mongo_models.Object)
    mongo_db.query().get_or_create(
        mongo_detections, model=mongo_models.Detection
    )
    mongo_db.query().get_or_create(
        mongo_detections_2, model=mongo_models.Detection
    )
    mongo_db.query().get_or_create(
        mongo_non_detections, model=mongo_models.NonDetection
    )


if __name__ == "__main__":
    wait_for_service(timeout=30, pause=1, callback=psql_ready, service="PSQL")
    wait_for_service(
        timeout=30, pause=1, callback=mongo_ready, service="Mongo"
    )
    insert_psql_data()
    insert_mongo_data()
