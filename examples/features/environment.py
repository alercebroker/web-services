from db_plugins.db.mongo.connection import MongoDatabaseCreator
from db_plugins.db.mongo import models
import signal
import time
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "a_secret_key"  # from text/config.yml
MONGO_SETTINGS = {
    "HOST": "mongo",
    "DATABASE": "database",
    "USERNAME": "mongo",
    "PASSWORD": "mongo",
    "PORT": 27017,
}

BASE_URL = "http://alerts_api:5000/"


def build_admin_token():
    token = {
        "access": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["admin"],
        "filters": [],
    }
    encripted_token = jwt.encode(token, SECRET_KEY, algorithm="HS256")
    return encripted_token


HEADER_ADMIN_TOKEN = {"AUTH-TOKEN": build_admin_token()}


def mongo_ready():
    try:
        mongo_db = MongoDatabaseCreator().create_database()
        mongo_db.connect(MONGO_SETTINGS)
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


def before_scenario(context, scenario):
    creator = MongoDatabaseCreator()
    context.mongo_db = creator.create_database()
    context.mongo_db.connect(MONGO_SETTINGS)
    context.mongo_db.create_db()


def after_scenario(context, scenario):
    tear_down_mongo(context.mongo_db)


def tear_down_mongo(db):
    db.drop_db()


def insert_in_database(context, model, **kwargs):
    if model == "detections":
        defaults = dict(
            aid="ALERCE",
            oid="OID",
            candid="CANDID",
            tid="TID",
            mjd=1.,
            fid=1,
            ra=80.,
            dec=120.,
            rb=1.,
            mag=1.,
            e_mag=1.,
            rfid=1,
            e_ra=1.,
            e_dec=1.,
            isdiffpos=1,
            corrected=True,
            parent_candid="",
            has_stamp=False,
            step_id_corr="",
            rbversion="",
        )
        defaults.update({key: type(defaults[key])(value) for key, value in kwargs.items()})
        detection = models.Detection(**defaults)
        context.mongo_db.query().get_or_create(detection, model=models.Detection)
