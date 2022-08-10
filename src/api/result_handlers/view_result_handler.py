from werkzeug.exceptions import NotFound, InternalServerError
from shared.error.exceptions import EmptyQuery, WrapperException
from shared.interface.command import ResultHandler
from flask import current_app


class ViewResultHandler(ResultHandler):
    def __init__(self):
        self.result = None

    def handle_success(self, result):
        self.result = result

    def handle_client_error(self, exception: WrapperException):
        current_app.logger.error(exception)
        if isinstance(exception.original_exception, EmptyQuery):
            raise NotFound()

    def handle_server_error(self, exception: WrapperException):
        current_app.logger.exception(exception)
        raise InternalServerError()
