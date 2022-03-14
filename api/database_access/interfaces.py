
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
    query_result = psql_db.query(psql_models.Object).filter(psql_models.Object.oid == object_id).one_or_none()

    if query_result:
      return query_result
    else:
      raise Exception(f"object {object_id} not found")

  @classmethod  
  def get_light_curve(cls, object_id):
    astro_obj = cls._get_object_by_id(object_id)

    light_curve = astro_obj.get_lightcurve()
    for det in light_curve["detections"]:
      det.phase = 0  # (det.mjd % obj.period) / obj.period
    
    return light_curve

  @classmethod
  def get_detections(cls, object_id):
    astro_obj = cls._get_object_by_id(object_id)

    return astro_obj.detections

  @classmethod
  def get_non_detections(cls, object_id):
    astro_obj = cls._get_object_by_id(object_id)

    return astro_obj.non_detections


class MongoInterface(DBInterface):

  @classmethod
  def get_light_curve(cls, object_id):
    light_curve = {
      "detections": cls.get_detections(object_id),
      "non_detections": cls.get_non_detections(object_id)
    }

    ''' from psql get light curve
    for det in light_curve["detections"]:
      det.phase = 0  # (det.mjd % obj.period) / obj.period
    '''
    return light_curve

  @classmethod
  def get_detections(cls, object_id):
    detections = mongo_db.query().find_all(
      model=mongo_models.Detection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    if detections:
      return list(detections)
    else:
      raise Exception(f"object {object_id} not found")

  @classmethod
  def get_non_detections(cls, object_id):
    non_detections = mongo_db.query().find_all(
      model=mongo_models.NonDetection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    if non_detections:
      return list(non_detections)
    else:
      raise Exception(f"object {object_id} not found")
