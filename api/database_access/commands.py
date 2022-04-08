from .interfaces import PSQLInterface, MongoInterface
from ..result_handlers.helper_functions import is_failure, is_success
from ..result_handlers.exceptions import (
    ClientErrorException,
    ServerErrorException,
    InterfaceNotFound,
)


ZTF_SURVEY_ID = "ztf"
ATLAS_SURVEY_ID = "atlas"

DATABASE_INTERFACES = {
    ZTF_SURVEY_ID: PSQLInterface,
    ATLAS_SURVEY_ID: MongoInterface,
}


class BaseCommand(object):
    def __init__(self, payload, survey_id, result_handler) -> None:
        self.survey_id = survey_id
        self.result_handler = result_handler
        self.payload = payload
        self.method = None

    def database_interface_selector(self):
        db_interface = DATABASE_INTERFACES.get(self.survey_id)

        if db_interface:
            return db_interface()
        else:
            raise InterfaceNotFound(self.survey_id)

    def execute(self):
        database_interface = self.database_interface_selector()
        query_result = database_interface.get_interface_query(self.method)(self.payload["object_id"])
        if is_success(query_result):
            self.result_handler.handle_success(query_result)
        else:
            exception = query_result.failure()
            if isinstance(exception, ClientErrorException):
                self.result_handler.handle_client_error(query_result)
            elif isinstance(exception, ServerErrorException):
                self.result_handler.handle_server_error(query_result)
            else:
                raise query_result.failure()


class GetLightCurve(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__({"object_id": object_id}, survey_id, result_handler)
        self.method = "get_light_curve"


class GetDetections(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__({"object_id": object_id}, survey_id, result_handler)
        self.object_id = object_id
        self.method = "get_detections"


class GetNonDetections(BaseCommand):

    def __init__(self, object_id, survey_id, result_handler) -> None:
        super().__init__({"object_id": object_id}, survey_id, result_handler)
        self.object_id = object_id
        self.method = "get_non_detections"

