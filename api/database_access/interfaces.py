
from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from .psql_db import db as psql_db
from .mongo_db import db as mongo_db


class ObjectNotFound(Exception):
  """
  Exception for empty queries for object data.
  Revelevan for any api with the object/<id> path.

  Attributes:
    object_id : the id of the object searched
    survey_id : the id of the survey in wich the oid was searched
  """
  def __init__(self, object_id, survey_id) -> None:
      super().__init__()
      self.object_id = object_id
      self.survey_id = survey_id

  def __str__(self) -> str:
      return f"Object {self.object_id} Not Found in survey {self.survey_id}"


class DBInterface(object):
  
  @classmethod
  def get_light_curve(cls, object_id):
    raise NotImplementedError()

  @classmethod
  def get_detections(cls, object_id):
    raise NotImplementedError()

  @classmethod
  def get_non_detections(cls, object_id):
    raise NotImplementedError()


class PSQLInterface(DBInterface):
  survey_id = "ztf"

  @classmethod
  def _get_object_by_id(cls, object_id):
    query_result = psql_db.query(psql_models.Object).filter(psql_models.Object.oid == object_id).one_or_none()

    if query_result:
      return query_result
    else:
      raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)

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
  survey_id = "atlas"

  @classmethod
  def get_light_curve(cls, object_id):
    light_curve = {
      "detections": cls.get_detections(object_id),
      "non_detections": cls._get_non_detections(object_id)
    }

    for det in light_curve["detections"]:
      det["phase"] = 0  # (det.mjd % obj.period) / obj.period

    return light_curve

  @classmethod
  def get_detections(cls, object_id):
    """
      There is no object without detections
    """
    detections = mongo_db.query().find_all(
      model=mongo_models.Detection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    if detections:
      detections = list(detections)
      if len(detections) > 0:
        return list(detections)
      else:
        raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)  
    else:
      raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)

  @classmethod
  def _get_non_detections(cls, object_id):
    non_detections = mongo_db.query().find_all(
      model=mongo_models.NonDetection,
      filter_by={
        "oid": object_id
      },
      paginate=False
    )

    return list(non_detections)

  @classmethod
  def get_non_detections(cls, object_id):
    non_detections = cls._get_non_detections(object_id)
    
    if len(non_detections) > 0:
      return non_detections
    else:
      raise ObjectNotFound(object_id=object_id, survey_id=cls.survey_id)
