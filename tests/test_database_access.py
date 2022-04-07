from unittest.mock import patch
import pytest
from api.database_access.control import DBControl
from api.database_access.commands import (
    GetLightCurve,
    GetDetections,
    GetNonDetections,
    BaseCommand,
)
from api.database_access.commands import InterfaceNotFound
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
