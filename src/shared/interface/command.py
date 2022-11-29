from returns.pipeline import is_successful
from returns.result import Result
from shared.error.exceptions import ClientErrorException, ServerErrorException


class ResultHandler:
    def handle_success(self, result):
        raise NotImplementedError()

    def handle_client_error(self, error: Exception):
        raise NotImplementedError()

    def handle_server_error(self, error: Exception):
        raise NotImplementedError()


class Command:
    def __init__(self, service, payload, handler: ResultHandler):
        self.service = service
        self.action = None
        self.payload = payload
        self.handler = handler

    def execute(self):
        action = getattr(self.service, self.action)
        result = action(self.payload)
        self._post_execute(result)

    def _post_execute(self, result) -> None:
        if is_successful(result):
            self.handler.handle_success(result.unwrap())
        else:
            exception = result.failure()
            if isinstance(exception, ClientErrorException):
                self.handler.handle_client_error(exception)
            elif isinstance(exception, ServerErrorException):
                self.handler.handle_server_error(exception)
            else:
                raise exception
