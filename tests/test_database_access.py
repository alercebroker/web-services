from platform import python_branch
import pytest
from conftest import db, models, mongo_db, mongo_models
from api.database_access.commands import  GetLightCurve, GetDetections, GetNonDetections, BaseCommand
from api.database_access.commands import InterfaceNotFound
from api.database_access.interfaces import DBInterface
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

def test_base_dbinterface(psql_service, client):
  with pytest.raises(NotImplementedError):
    DBInterface.get_light_curve("ATLAS1")
  
  with pytest.raises(NotImplementedError):
    DBInterface.get_detections("ATLAS1")

  with pytest.raises(NotImplementedError):
    DBInterface.get_non_detections("ATLAS1")