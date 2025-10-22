import traceback
import logging

from fastapi import HTTPException

from core.exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
)


def handle_success(result):
    return result


def _handle_client_error(err: BaseException, code=400):
    raise HTTPException(status_code=code, detail=str(err))


def _handle_server_error(err: BaseException):
    if err.__traceback__:
        traceback.print_exception(err)
    logging.error(err)
    raise HTTPException(status_code=500, detail=str(err))


def handle_error(err: BaseException):
    if isinstance(err, DatabaseError):
        _handle_server_error(err)
    if isinstance(err, SurveyIdError):
        _handle_client_error(err)
    if isinstance(err, AtlasNonDetectionError):
        _handle_client_error(err)
    if isinstance(err, ObjectNotFound):
        _handle_client_error(err, code=404)
