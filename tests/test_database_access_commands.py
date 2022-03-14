from conftest import db, models, mongo_db, mongo_models
from api.database_access.commands import  GetLightCurve, GetDetections, GetNonDetections

ZTF_ID = "ztf"
ATLAS_ID = "atlas"

def test_get_light_curve_mongo(psql_service, client):
  command = GetLightCurve("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result["detections"]) == 1
  assert result["detections"][0]["oid"] == "ATLAS1"

  assert len(result["non_detections"]) == 1
  assert result["non_detections"][0]["oid"] == "ATLAS1"

def test_get_light_curve_psql(psql_service, client):
  command = GetLightCurve("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result["detections"]) == 1

  assert len(result["non_detections"]) == 1

def test_get_light_curve_not_found(psql_service, client):
  pass

def test_get_detections_mongo(psql_service, client):
  command = GetDetections("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_detections_psql(psql_service, client):
  command = GetDetections("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_detections_not_found(psql_service, client):
  pass

def test_get_non_detections_mongo(psql_service, client):
  command = GetNonDetections("ATLAS1", ATLAS_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_non_detections_psql(psql_service, client):
  command = GetNonDetections("ZTF1", ZTF_ID)
  result = command.execute()

  assert len(result) == 1

def test_get_non_detections_not_found(psql_service, client):
  pass