from werkzeug.exceptions import NotFound, InternalServerError, BadRequest
from ..result_handlers.exceptions import (
    ClientErrorException,
    ServerErrorException,
    InterfaceNotFound,
    ObjectNotFound,
)


class ViewResultHandler(object): 

    def __init__(self, callbacks_dict={}):
        self.callbacks = callbacks_dict
        self.result_operation = None

    def get_result(self):
        return self.result_operation()

    def handle_success(self, result):
        self.result_operation = result.unwrap
    
    def handle_client_error(self, result):
        exception = result.failure()
        if isinstance(exception.original_exception, ObjectNotFound):
            raise NotFound()

    def handle_server_error(self, result):
        raise InternalServerError()


