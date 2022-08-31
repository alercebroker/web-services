from db_plugins.db.mongo.connection import MongoDatabaseCreator
from db_plugins.db.mongo import models
import signal
import time


def mongo_ready():
    try:
        mongo_db = MongoDatabaseCreator().create_database()
        settings = {
            "HOST": "mongo",
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


def before_all(context):
    wait_for_service(
        timeout=30, pause=1, callback=mongo_ready, service="Mongo"
    )
    context.db_created = "YES"


def after_scenario(context, scenario):
    tear_down_mongo(context.mongo_db)


def tear_down_mongo(db):
    db.drop_db()


def insert_mongo_data(context):
    creator = MongoDatabaseCreator()
    context.mongo_db = creator.create_database()
    settings = {
        "HOST": "mongo",
        "DATABASE": "database",
        "USERNAME": "mongo",
        "PASSWORD": "mongo",
        "PORT": 27017,
    }
    context.mongo_db.connect(settings)
    context.mongo_db.create_db()
    mongo_object = models.Object(
        aid="AID1",
        oid=["ATLAS1"],
        lastmjd="lastmjd",
        firstmjd="firstmjd",
        meanra=100.0,
        meandec=50.0,
        ndet="ndet",
    )
    mongo_object_2 = models.Object(
        aid="AID2",
        oid=["ATLAS2", "ZTF1"],
        lastmjd="lastmjd",
        firstmjd="firstmjd",
        meanra=100.0,
        meandec=50.0,
        ndet="ndet",
    )
    mongo_detections = models.Detection(
        tid="ATLAS01",
        aid="AID1",
        oid="ATLAS1",
        candid="candid",
        mjd=1,
        fid=1,
        ra=1,
        dec=1,
        rb=1,
        mag=1,
        e_mag=1,
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
    mongo_detections_2 = models.Detection(
        tid="ZTF02",
        aid="AID2",
        oid="ZTF1",
        candid="candid",
        mjd=1,
        fid=1,
        ra=1,
        dec=1,
        rb=1,
        mag=1,
        e_mag=1,
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
    mongo_detections_3 = models.Detection(
        tid="ATLAS02",
        aid="AID2",
        oid="ATLAS2",
        candid="candid",
        mjd=1,
        fid=1,
        ra=1,
        dec=1,
        rb=1,
        mag=1,
        e_mag=1,
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
    mongo_non_detections = models.NonDetection(
        aid="AID2",
        oid="ZTF1",
        tid="ZTF",
        mjd=1,
        diffmaglim=1,
        fid=1,
    )
    context.mongo_db.query().get_or_create(
        mongo_object, model=models.Object
    )
    context.mongo_db.query().get_or_create(
        mongo_object_2, model=models.Object
    )
    context.mongo_db.query().get_or_create(
        mongo_detections, model=models.Detection
    )
    context.mongo_db.query().get_or_create(
        mongo_detections_2, model=models.Detection
    )
    context.mongo_db.query().get_or_create(
        mongo_detections_3, model=models.Detection
    )
    context.mongo_db.query().get_or_create(
        mongo_non_detections, model=models.NonDetection
    )
