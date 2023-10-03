from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models import Detection, NonDetection
from pymongo.database import Database
from returns.pipeline import is_successful
from returns.result import Failure, Success
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
)
from .models import Detection as DetectionModel
from .models import NonDetection as NonDetectionModel


def default_handle_success(result):
    return result


def default_handle_error(error):
    raise error


def fail_from_list(failable_list: list):
    for el in failable_list:
        if not is_successful(el):
            return el.failure()

def get_lightcurve(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[..., dict] = default_handle_success,
    handle_error: Callable[Exception, None] = default_handle_error,
) -> dict:
    if survey_id == "ztf":
        detections = _get_detections_sql(session_factory, oid, tid=survey_id)
        non_detections = _get_non_detections_sql(session_factory, oid, tid=survey_id)
    elif survey_id == "atlas":
        detections = _get_detections_mongo(mongo_db, oid, tid="atlas")
        non_detections = Success([])
    else:
        handle_error(SurveyIdError(survey_id))
    failure = fail_from_list([detections, non_detections])
    if not failure:
        return handle_success(
            {
                "detections": detections.unwrap(),
                "non_detections": non_detections.unwrap(),
            }
        )
    else:
        handle_error(failure)


def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[..., dict] = default_handle_success,
    handle_error: Callable[Exception, None] = default_handle_error,
) -> list:
    if survey_id in ["ztf", "atlas"]:
        sql_detections_result = _get_detections_sql(session_factory, oid, tid=survey_id)
        if not is_successful(sql_detections_result):
            handle_error(sql_detections_result.failure())
        sql_detections = sql_detections_result.unwrap()

        mongo_detections_result = _get_detections_mongo(mongo_db, oid, tid=survey_id)
        if not is_successful(mongo_detections_result):
            handle_error(mongo_detections_result.failure())
        mongo_detections = mongo_detections_result.unwrap()

        detections = sql_detections + mongo_detections
        return handle_success(detections)
    else:
        handle_error(SurveyIdError(survey_id))



def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[..., dict] = default_handle_success,
    handle_error: Callable[Exception, None] = default_handle_error,
):
    if survey_id == "ztf":
        sql_non_detections_result = _get_non_detections_sql(session_factory, oid, tid=survey_id)
        if not is_successful(sql_non_detections_result):
            handle_error(sql_non_detections_result.failure())
        sql_non_detections = sql_non_detections_result.unwrap()

        mongo_non_detections_result = _get_non_detections_mongo(mongo_db, oid, tid=survey_id)
        if not is_successful(mongo_non_detections_result):
            handle_error(mongo_non_detections_result.failure())
        mongo_non_detections = mongo_non_detections_result.unwrap()

        non_detections = sql_non_detections + mongo_non_detections
        return handle_success(non_detections)

    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id))


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str,
    tid: str
) -> Success[list[DetectionModel]] | Failure:
    if tid == "atlas":
        return Success([])
    try:
        with session_factory() as session:
            stmt = select(Detection, text("'ztf'")).filter(
                Detection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                _ztf_detection_to_multistream(res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return Success(result)
    except Exception as e:
        return Failure(DatabaseError(e))


def _get_detections_mongo(
    database: Database, oid: str, tid: str
) -> Success[list[DetectionModel]] | Failure:
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["detection"].find({"aid": obj["_id"], "tid": tid})
        result = [DetectionModel(**res, candid=res["_id"]) for res in result]
        return Success(result)
    except ValueError as e:
        return Failure(ObjectNotFound(oid))
    except Exception as e:
        return Failure(DatabaseError(e))


def _get_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str,
    tid: str
) -> Success[list[NonDetectionModel]] | Failure:
    if tid == "atlas":
        return Success([])
    try:
        with session_factory() as session:
            stmt = select(NonDetection, text("'ztf'")).where(
                NonDetection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                _ztf_non_detection_to_multistream(res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return Success(result)
    except Exception as e:
        return Failure(DatabaseError(e))

def _get_non_detections_mongo(
    database: Database, oid: str, tid: str
) -> Success[list[NonDetectionModel]] | Failure:
    if tid == "atlas":
        return Success([])
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["non_detection"].find({"aid": obj["_id"], "tid": tid})
        result = [NonDetectionModel(**res) for res in result]
        return Success(result)
    except ValueError as e:
        return Failure(ObjectNotFound(oid))
    except Exception as e:
        return Failure(DatabaseError(e))

def _ztf_detection_to_multistream(
    detection: dict[str, any],
    tid: str,
) -> DetectionModel:
    """Converts a dictionary representing a detection in the ZTF schema
    to the Multistream schema defined in models.py. Separates every field
    that's without a correspondence in the schema into extra_fields.
    :param detection: Dictionary representing a detection.
    :param tid: Telescope id for this detection.
    :return: A Detection with the converted data."""
    fields = {
        "candid",
        "oid",
        "sid",
        "aid",
        "tid",
        "mjd",
        "fid",
        "ra",
        "e_ra",
        "dec",
        "e_dec",
        "magpsf",
        "sigmapsf",
        "magpsf_corr",
        "sigmapsf_corr",
        "sigmapsf_corr_ext",
        "isdiffpos",
        "corrected",
        "dubious",
        "parent_candid",
        "has_stamp",
    }

    extra_fields = {}
    for field, value in detection.items():
        if field not in fields and not field.startswith("_"):
            extra_fields[field] = value

    return DetectionModel(
        **detection,
        tid=tid,
        mag=detection["magpsf"],
        e_mag=detection["sigmapsf"],
        mag_corr=detection.get("magpsf_corr", None),
        e_mag_corr=detection.get("sigmapsf_corr", None),
        e_mag_corr_ext=detection.get("sigmapsf_corr_ext", None),
        extra_fields=extra_fields,
    )


def _ztf_non_detection_to_multistream(
    non_detections: dict[str, any],
    tid: str,
) -> NonDetectionModel:
    """Converts a dictionary representing a non detection in the ZTF schema
    to the Multistream schema defined in models.py.
    :param non_detection: Dictionary representing a non_detection.
    :param tid: Telescope id for this detection.
    :return: A NonDetection with the converted data."""
    return NonDetectionModel(
        tid=tid,
        oid=non_detections["oid"],
        mjd=non_detections["mjd"],
        fid=non_detections["fid"],
        diffmaglims=non_detections.get("diffmaglim", None),
    )
