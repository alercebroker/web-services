from werkzeug.exceptions import NotFound, InternalServerError
from shared.error.exceptions import ObjectNotFound
from flask import current_app


def default_callback(result):
    return result


class ViewResultHandler:
    def __init__(self, callback=default_callback):
        self.result = None
        self.callback = callback

    def handle_success(self, result):
        self.result = self.callback(result)

    def handle_client_error(self, exception: Exception):
        current_app.logger.error(exception)
        if isinstance(exception.original_exception, ObjectNotFound):
            raise NotFound()

    def handle_server_error(self, exception: Exception):
        current_app.logger.exception(exception)
        raise InternalServerError(original_exception=exception)
