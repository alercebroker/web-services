
from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from .psql_db import db as psql_db
from .mongo_db import db as mongo_db

class DBInterface(object):
  
  def get_light_curve(object_id):
    raise NotImplemented()

  def get_detections(object_id):
    raise NotImplemented()

  def get_non_detections(object_id):
    raise NotImplemented()


class PSQLInterface(DBInterface):

  @classmethod
  def _get_object_by_id(cls, object_id):
    print(f"Geting object {object_id}")
    query_result = psql_db.query(psql_models.Object).filter(psql_models.Object.oid == id).one_or_none()

    if query_result:
      return query_result
    else:
      raise Exception(f"object {object_id} not found")

  @classmethod  
  def get_light_curve(cls, object_id):
    print(f"getting PSQL light curve {object_id}")
    astro_obj = cls.get_object_by_id(object_id,)

    light_curve = astro_obj.get_lightcurve()
    for det in light_curve["detections"]:
      det.phase = 0  # (det.mjd % obj.period) / obj.period
    
    return light_curve

  @classmethod
  def get_detections(cls, object_id):
    print(f"getting PSQL light curve detections for {object_id}")
    astro_obj = cls.get_object_by_id(object_id,)

    return astro_obj.detections

  @classmethod
  def get_non_detections(cls, object_id):
    print(f"getting PSQL light curve detections for {object_id}")
    astro_obj = cls.get_object_by_id(object_id,)

    return astro_obj.non_detections


class MongoInterface(DBInterface):

  @classmethod
  def get_light_curve(cls, object_id):
    print(f"getting MONGO light curve for {object_id}")
    light_curve = {
      "detectioins": cls.get_light_curve_detections(object_id),
      "non_detections": cls.get_light_curve_non_detections(object_id)
    }

    for det in light_curve["detections"]:
      det.phase = 0  # (det.mjd % obj.period) / obj.period

    return light_curve

  @classmethod
  def get_detections(cls, object_id):
    print(f"getting MONGO light curve detections for {object_id}")
    detections = mongo_db.query().find_one(
      model=mongo_models.Detection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    if detections:
      return detections
    else:
      raise Exception(f"object {object_id} not found")

  @classmethod
  def get_non_detections(cls, object_id):
    print(f"getting MONGO light curve non detections for {object_id}")
    non_detections = mongo_db.query().find_one(
      model=mongo_models.NonDetection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    if non_detections:
      return non_detections
    else:
      raise Exception(f"object {object_id} not found")
