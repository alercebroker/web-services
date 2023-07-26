from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.sql_models import Detection, NonDetection
from returns.result import Success, Failure
from returns.pipeline import is_successful
from .exceptions import (
    DatabaseError,
)
from pymongo.database import Database


def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
):
    if survey_id == "ztf":
        result = _get_detections_sql(session_factory, oid)
        if is_successful(result):
            return result.unwrap()
        else:
            exception = result.failure()
            raise exception

    elif survey_id == "atlas":
        result = _get_detections_mongo(mongo_db, oid)
        if is_successful(result):
            return result.unwrap()
        else:
            raise result.failure()

    else:
        raise Exception(
            f"Can't retrieve detections survey id not recognized {survey_id}"
        )


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
):
    if survey_id == "ztf":
        result = _get_non_detections_sql(session_factory, oid)
        if is_successful(result):
            return result.unwrap()
        else:
            # TODO make better error handling here
            exception = result.failure()
            raise exception
    elif survey_id == "atlas":
        raise Exception(
            "Can't retrieve non detections: ATLAS does not provide non_detections"
        )
    else:
        raise Exception(
            f"Can't retrieve non detections: survey id not recognized {survey_id}"
        )


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
):
    try:
        with session_factory() as session:
            stmt = select(Detection).where(Detection.oid == oid)
            result = session.execute(stmt)
            result = [res for res in result.scalars()]
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
            stmt = select(NonDetection).where(NonDetection.oid == oid)
            result = session.execute(stmt)
            result = [res for res in result.scalars()]
            return Success(result)
    except Exception as e:
        return Failure(DatabaseError(e))
