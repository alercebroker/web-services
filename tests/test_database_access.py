from unittest.mock import patch
import pytest
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest
from api.database_access.control import DBControl
from api.database_access.commands import (
    ATLAS_SURVEY_ID,
    ZTF_SURVEY_ID,
    GetLightCurve,
    GetDetections,
    GetNonDetections,
    BaseCommand,
)

from db_plugins.db.mongo import MongoConnection
from db_plugins.db.sql import SQLConnection
from api.result_handlers.view_result_handlers import ViewResultHandler
from api.database_access.interfaces import (
    DBInterface,
    PSQLInterface,
    MongoInterface,
)
from api.result_handlers.exceptions import (
    InterfaceNotFound
)


ZTF_ID = "ztf"
ATLAS_ID = "atlas"


def test_base_command_interface_selector(mongo_service, psql_service, client):
    with pytest.raises(InterfaceNotFound):
        command = BaseCommand("Error", None)
        command.database_interface_selector()

    command = BaseCommand(ZTF_ID, None)
    db_interface = command.database_interface_selector()
    assert isinstance(db_interface, PSQLInterface)

    command = BaseCommand(ATLAS_ID, None)
    db_interface = command.database_interface_selector()
    assert isinstance(db_interface, MongoInterface)


def test_base_dbinterface(mongo_service, psql_service, client):
    with pytest.raises(NotImplementedError):
        DBInterface.get_light_curve("ATLAS1")

    with pytest.raises(NotImplementedError):
        DBInterface.get_detections("ATLAS1")

    with pytest.raises(NotImplementedError):
        DBInterface.get_non_detections("ATLAS1")


def test_control_connect(mongo_service, psql_service, client):

    with patch.object(DBControl, "connect_psql") as mock_connect_psql:
        with patch.object(DBControl, "connect_mongo") as mock_connect_mongo:
            test_app_config = {"CONNECT_PSQL": True, "CONNECT_MONGO": True}
            db_control = DBControl(test_app_config, {}, {})
            db_control.connect_databases()

            mock_connect_psql.assert_called_once()
            mock_connect_mongo.assert_called_once()

    with patch.object(DBControl, "connect_psql") as mock_connect_psql:
        with patch.object(DBControl, "connect_mongo") as mock_connect_mongo:
            test_app_config = {"CONNECT_PSQL": True, "CONNECT_MONGO": False}
            db_control = DBControl(test_app_config, {}, {})
            db_control.connect_databases()

            mock_connect_psql.assert_called_once()
            mock_connect_mongo.assert_not_called()

    with patch.object(DBControl, "connect_psql") as mock_connect_psql:
        with patch.object(DBControl, "connect_mongo") as mock_connect_mongo:
            test_app_config = {"CONNECT_PSQL": False, "CONNECT_MONGO": True}
            db_control = DBControl(test_app_config, {}, {})
            db_control.connect_databases()

            mock_connect_psql.assert_not_called()
            mock_connect_mongo.assert_called_once()


def test_control_cleanup(mongo_service, psql_service, client):

    with patch.object(DBControl, "cleanup_psql") as mock_cleanup_psql:
        with patch.object(DBControl, "cleanup_mongo") as mock_cleanup_mongo:
            test_app_config = {"CONNECT_PSQL": True, "CONNECT_MONGO": True}
            db_control = DBControl(test_app_config, {}, {})
            db_control.cleanup_databases("")

            mock_cleanup_psql.assert_called_once()
            mock_cleanup_mongo.assert_called_once()

    with patch.object(DBControl, "cleanup_psql") as mock_cleanup_psql:
        with patch.object(DBControl, "cleanup_mongo") as mock_cleanup_mongo:
            test_app_config = {"CONNECT_PSQL": True, "CONNECT_MONGO": False}
            db_control = DBControl(test_app_config, {}, {})
            db_control.cleanup_databases("")

            mock_cleanup_psql.assert_called_once()
            mock_cleanup_mongo.assert_not_called()

    with patch.object(DBControl, "cleanup_psql") as mock_cleanup_psql:
        with patch.object(DBControl, "cleanup_mongo") as mock_cleanup_mongo:
            test_app_config = {"CONNECT_PSQL": False, "CONNECT_MONGO": True}
            db_control = DBControl(test_app_config, {}, {})
            db_control.cleanup_databases("")

            mock_cleanup_psql.assert_not_called()
            mock_cleanup_mongo.assert_called_once()

def test_get_light_curve_unexpected_exception(mongo_service, psql_service, client):
    with patch.object(MongoConnection, "query") as mongo_connection_mock:
        mongo_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetLightCurve("ATLAS1", ATLAS_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

    with patch.object(SQLConnection, "query") as psql_connection_mock:
        psql_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetLightCurve("ZTF1", ZTF_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

def test_get_detections_unexpected_exception(mongo_service, psql_service, client):
    with patch.object(MongoConnection, "query") as mongo_connection_mock:
        mongo_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetDetections("ATLAS1", ATLAS_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

    with patch.object(SQLConnection, "query") as psql_connection_mock:
        psql_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetDetections("ZTF1", ZTF_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

def test_get_non_detections_unexpected_exception(mongo_service, psql_service, client):

    with patch.object(SQLConnection, "query") as psql_connection_mock:
        psql_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetNonDetections("ZTF1", ZTF_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

    with patch.object(MongoConnection, "query") as mongo_connection_mock:
        mongo_connection_mock.side_effect = Exception("unexpected error")
        result_handler = ViewResultHandler()
        command = GetNonDetections("ATLAS1", ATLAS_SURVEY_ID, result_handler)
        with pytest.raises(InternalServerError):
            command.execute()

def test_get_lightcurve_no_interface_exception(mongo_service, psql_service, client):

    with patch.object(GetLightCurve, "database_interface_selector") as db_interface_selector_mock:
        db_interface_selector_mock.side_effect = InterfaceNotFound("error")
        result_handler = ViewResultHandler()
        command = GetLightCurve("ZTF1", ZTF_SURVEY_ID, result_handler)
        with pytest.raises(InterfaceNotFound):
            command.execute()
