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
    if survey_id in ["ztf", "atlas"]:
        detections = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        non_detections = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
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
        detections_result = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(detections_result):
        return handle_success(detections_result.unwrap())
    else:
        handle_error(detections_result.failure())


def _get_all_unique_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
) -> Success[list[DetectionModel]] | Failure:
    try:
        sql_detections = _get_detections_sql(
            session_factory, oid, tid=survey_id
        )
        mongo_detections = _get_detections_mongo(mongo_db, oid, tid=survey_id)
    except (DatabaseError, ObjectNotFound) as e:
        return Failure(e)

    detections = list(set(sql_detections + mongo_detections))
    return Success(detections)


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[..., dict] = default_handle_success,
    handle_error: Callable[Exception, None] = default_handle_error,
) -> list:
    if survey_id == "ztf":
        non_detections_result = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(non_detections_result):
        return handle_success(non_detections_result.unwrap())
    else:
        handle_error(non_detections_result.failure())


def _get_all_unique_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
) -> Success[list[NonDetectionModel]] | Failure:
    try:
        sql_non_detections = _get_non_detections_sql(
            session_factory, oid, tid=survey_id
        )
        mongo_non_detections = _get_non_detections_mongo(
            mongo_db, oid, tid=survey_id
        )

        non_detections = list(set(sql_non_detections + mongo_non_detections))
        return Success(non_detections)
    except (DatabaseError, ObjectNotFound) as e:
        return Failure(e)


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[DetectionModel]:
    if tid == "atlas":
        return []
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
            return result
    except Exception as e:
        raise DatabaseError(e)


def _get_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[DetectionModel]:
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["detection"].find({"aid": obj["_id"], "tid": tid})
        result = [DetectionModel(**res, candid=res["_id"]) for res in result]
        return result
    except ValueError as e:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e)


def _get_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[NonDetectionModel]:
    if tid == "atlas":
        return []
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
            return result
    except Exception as e:
        raise DatabaseError(e)


def _get_non_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[NonDetectionModel]:
    if tid == "atlas":
        return []
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["non_detection"].find(
            {"aid": obj["_id"], "tid": tid}
        )
        result = [NonDetectionModel(**res) for res in result]
        return result
    except ValueError as e:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e)


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
        aid=non_detections.get("aid", None),
        tid=tid,
        sid=non_detections.get("sid", None),
        oid=non_detections["oid"],
        mjd=non_detections["mjd"],
        fid=non_detections["fid"],
        diffmaglim=non_detections.get("diffmaglim", None),
    )
