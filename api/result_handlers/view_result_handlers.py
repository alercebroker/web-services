from http import HTTPStatus
from werkzeug.exceptions import NotFound, InternalServerError

class ViewResultHandler(object): 

    def __init__(self, response_object, callbacks_dict={}):
        self.response_object = response_object
        self.callbacks = callbacks_dict

    def handle_success(self, result):
        #result_value = result.unwrap()
        #self.response_object.set_data(result_value)
        #self.response_object.status = HTTPStatus.OK.name
        #self.response_object.status_code = HTTPStatus.OK.value
        self.response_object = result.unwrap()
    
    def handle_client_error(self, result):
        self.response_object.status = HTTPStatus.NOT_FOUND.name
        self.response_object.status_code = HTTPStatus.NOT_FOUND.value

    def handle_server_error(self, result):
        self.response_object.status = HTTPStatus.INTERNAL_SERVER_ERROR.name
        self.response_object.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value


class ViewResultHandler2(object): 

    def __init__(self, response_object, callbacks_dict={}):
        self.response_object = response_object
        self.callbacks = callbacks_dict
        self.get_result = None

    def handle_success(self, result):
        def return_result():
            return result.unwrap()
        self.get_result = return_result
    
    def handle_client_error(self, result):
        def raise_not_found():
            raise NotFound()
        self.get_result = raise_not_found

    def handle_server_error(self, result):
        def raise_internal_server_error():
            raise InternalServerError()
        self.get_result = raise_internal_server_error


