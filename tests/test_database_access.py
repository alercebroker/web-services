from unittest.mock import patch
import pytest
from api.database_access.control import DBControl
from api.database_access.commands import  GetLightCurve, GetDetections, GetNonDetections, BaseCommand
from api.database_access.commands import InterfaceNotFound
from api.database_access.interfaces import DBInterface, PSQLInterface, MongoInterface
from api.database_access.interfaces import ObjectNotFound


ZTF_ID = "ztf"
ATLAS_ID = "atlas"

def test_get_light_curve_mongo(psql_service, client):
  command = GetLightCurve("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result["detections"]) == 1
  assert result["detections"][0]["oid"] == "ATLAS1"

  assert len(result["non_detections"]) == 1
  assert result["non_detections"][0]["oid"] == "ATLAS1"

  command = GetLightCurve("ATLAS2", ATLAS_ID)
  result = command.execute()

  assert len(result["detections"]) == 1
  assert result["detections"][0]["oid"] == "ATLAS2"

  assert len(result["non_detections"]) == 0
  assert result["non_detections"] == []

def test_get_light_curve_psql(psql_service, client):
  command = GetLightCurve("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result["detections"]) == 1

  assert len(result["non_detections"]) == 1

def test_get_light_curve_not_found(psql_service, client):
  with pytest.raises(ObjectNotFound):
    command = GetLightCurve("ZTF1", ATLAS_ID)
    command.execute()
  
  with pytest.raises(ObjectNotFound):
    command = GetLightCurve("ATLAS1", ZTF_ID)
    command.execute()

def test_get_detections_mongo(psql_service, client):
  command = GetDetections("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_detections_psql(psql_service, client):
  command = GetDetections("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_detections_not_found(psql_service, client):
  with pytest.raises(ObjectNotFound):
    command = GetDetections("ATLAS1", ZTF_ID)
    command.execute()
  
  with pytest.raises(ObjectNotFound):
    command = GetDetections("ZTF1", ATLAS_ID)
    command.execute()

def test_get_non_detections_mongo(psql_service, client):
  command = GetNonDetections("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_non_detections_psql(psql_service, client):
  command = GetNonDetections("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_non_detections_not_found(psql_service, client):
  with pytest.raises(ObjectNotFound):
    command = GetNonDetections("ATLAS1", ZTF_ID)
    command.execute()
  
  command = GetNonDetections("ZTF1", ATLAS_ID)
  result = command.execute()

  assert len(result) == 0

def test_base_command_interface_selector(psql_service, client):
  with pytest.raises(InterfaceNotFound):
    command = BaseCommand("Error")
    command.database_interface_selector()

  command = BaseCommand(ZTF_ID)
  db_interface = command.database_interface_selector()
  assert isinstance(db_interface, PSQLInterface)

  command = BaseCommand(ATLAS_ID)
  db_interface = command.database_interface_selector()
  assert isinstance(db_interface, MongoInterface)

def test_base_dbinterface(psql_service, client):
  with pytest.raises(NotImplementedError):
    DBInterface.get_light_curve("ATLAS1")
  
  with pytest.raises(NotImplementedError):
    DBInterface.get_detections("ATLAS1")

  with pytest.raises(NotImplementedError):
    DBInterface.get_non_detections("ATLAS1")

def test_control_connect(psql_service, client):
  
  with patch.object(DBControl, 'connect_psql') as mock_connect_psql:
    with patch.object(DBControl, 'connect_mongo') as mock_connect_mongo:
      test_app_config = {
        "CONNECT_PSQL": True,
        "CONNECT_MONGO": True
      }
      db_control = DBControl(test_app_config, {}, {})
      db_control.connect_databases()

      mock_connect_psql.assert_called_once()
      mock_connect_mongo.assert_called_once()
  
  with patch.object(DBControl, 'connect_psql') as mock_connect_psql:
    with patch.object(DBControl, 'connect_mongo') as mock_connect_mongo:
      test_app_config = {
        "CONNECT_PSQL": True,
        "CONNECT_MONGO": False
      }
      db_control = DBControl(test_app_config, {}, {})
      db_control.connect_databases()

      mock_connect_psql.assert_called_once()
      mock_connect_mongo.assert_not_called()

  with patch.object(DBControl, 'connect_psql') as mock_connect_psql:
    with patch.object(DBControl, 'connect_mongo') as mock_connect_mongo:
      test_app_config = {
        "CONNECT_PSQL": False,
        "CONNECT_MONGO": True
      }
      db_control = DBControl(test_app_config, {}, {})
      db_control.connect_databases()

      mock_connect_psql.assert_not_called()
      mock_connect_mongo.assert_called_once()
