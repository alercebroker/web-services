from werkzeug.exceptions import NotFound, InternalServerError
from shared.error.exceptions import ObjectNotFound
from flask import current_app


class ViewResultHandler:
    def __init__(self):
        self.result = None

    def handle_success(self, result):
        self.result = result.unwrap()

    def handle_client_error(self, exception: Exception):
        current_app.logger.error(exception)
        if isinstance(exception.original_exception, ObjectNotFound):
            raise NotFound()

    def handle_server_error(self, exception: Exception):
        current_app.logger.exception(exception)
        raise InternalServerError()
