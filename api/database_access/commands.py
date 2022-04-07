from sre_constants import FAILURE
from .interfaces import PSQLInterface, MongoInterface
from ..result_handlers.helper_functions import is_failure, is_success
from ..result_handlers.exceptions import (
    InterfaceNotFound,
    SERVER_EXCEPTION_CODE,
    CLIENT_EXCEPTION_CODE
)


ZTF_SURVEY_ID = "ztf"
ATLAS_SURVEY_ID = "atlas"

DATABASE_INTERFACES = {
    ZTF_SURVEY_ID: PSQLInterface,
    ATLAS_SURVEY_ID: MongoInterface,
}


class BaseCommand(object):
    def __init__(self, survey_id, result_handler) -> None:
        self.survey_id = survey_id
        self.result_handler = result_handler
        self.method = None

    def database_interface_selector(self):
        db_interface = DATABASE_INTERFACES.get(self.survey_id)

        if db_interface:
            return db_interface()
        else:
            raise InterfaceNotFound(self.survey_id)

    def execute(self):
        database_interface = self.database_interface_selector()
        result = database_interface.get_interface_query(self.method)(self.object_id)
        if is_success(result):
            self.result_handler.handle_success(result)
        else:
            code = result.failure().code
            if code == CLIENT_EXCEPTION_CODE:
                self.result_handler.handle_client_error(result)
            else:
                self.result_handler.handle_server_error(result)



class GetLightCurve(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__(survey_id, result_handler)
        self.object_id = object_id
        self.method = "get_light_curve"


class GetDetections(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__(survey_id, result_handler)
        self.object_id = object_id
        self.method = "get_detections"


class GetNonDetections(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__(survey_id, result_handler)
        self.object_id = object_id
        self.method = "get_non_detections"

