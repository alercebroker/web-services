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


def _handle_client_error(err: Exception, code=400):
    raise HTTPException(status_code=code, detail=str(err))


def _handle_server_error(err: Exception):
    logging.error(err)
    raise HTTPException(status_code=500, detail=str(err))


def handle_error(err: Exception):
    if isinstance(err, DatabaseError):
        _handle_server_error(err)
    if isinstance(err, SurveyIdError):
        _handle_client_error(err)
    if isinstance(err, AtlasNonDetectionError):
        _handle_client_error(err)
    if isinstance(err, ObjectNotFound):
        _handle_client_error(err, code=404)
