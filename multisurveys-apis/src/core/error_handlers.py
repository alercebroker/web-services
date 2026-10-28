import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.exceptions import DatabaseError, ObjectNotFound

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI):
    @app.exception_handler(ObjectNotFound)
    def handle_object_not_found(request: Request, exc: ObjectNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DatabaseError)
    def handle_database_error(request: Request, exc: DatabaseError):
        logger.error("DatabaseError on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"detail": "Database error"})

    @app.exception_handler(ValueError)
    def handle_value_error(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    def handle_validation_error(request: Request, exc: ValidationError):
        logger.error("Model validation failed on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.exception_handler(Exception)
    def handle_unexpected(request: Request, exc: Exception):
        msg = str(exc)
        if "canceling statement" in msg or "statement timeout" in msg:
            logger.error("Query timeout on %s %s: %s", request.method, request.url.path, msg)
            return JSONResponse(status_code=504, content={"detail": "Query timed out"})
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
