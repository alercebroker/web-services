from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy import select, text
from returns.result import Success, Failure
from returns.pipeline import is_successful
from .exceptions import DatabaseError, SurveyIdError, AtlasNonDetectionError
from .models import (
    Detection as DetectionModel,
    NonDetection as NonDetectionModel,
)
from pymongo.database import Database
from db_plugins.db.sql.models import Detection, NonDetection
from sqlalchemy.orm import Session


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
        detections = _get_detections_sql(session_factory, oid)
        non_detections = _get_non_detections_sql(session_factory, oid)
    elif survey_id == "atlas":
        detections = _get_detections_mongo(mongo_db, oid)
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
    if survey_id == "ztf":
        result = _get_detections_sql(session_factory, oid)

    elif survey_id == "atlas":
        result = _get_detections_mongo(mongo_db, oid)
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(result):
        return handle_success(result.unwrap())
    else:
        handle_error(result.failure())


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[..., dict] = default_handle_success,
    handle_error: Callable[Exception, None] = default_handle_error,
):
    if survey_id == "ztf":
        result = _get_non_detections_sql(session_factory, oid)
        if is_successful(result):
            return handle_success(result.unwrap())
        else:
            return handle_error(result.failure())
    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id))


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
):
    try:
        with session_factory() as session:
            stmt = select(Detection, text("'ztf'")).filter(
                Detection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                DetectionModel(**res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return Success(result)
    except Exception as e:
        return Failure(DatabaseError(e))


def _get_detections_mongo(database: Database, oid: str):
    try:
        result = database["detection"].find({"oid": oid})
        return Success([res for res in result])
    except Exception as e:
        return Failure(DatabaseError(e))


def _get_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
):
    try:
        with session_factory() as session:
            stmt = select(NonDetection, text("'ztf'")).where(
                NonDetection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                NonDetectionModel(**res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return Success(result)
    except Exception as e:
        return Failure(DatabaseError(e))
