
from .interfaces import PSQLInterface, MongoInterface


class InterfaceNotFound(Exception):
  """
  Exception commands initialized with invalid surveys ids.
  The valid surey_ids are setted in configuration

  Attributes:
    survey_id : the id of the survey for the constructor
  """
  def __init__(self, survey_id) -> None:
      super().__init__()
      self.survey_id = survey_id

  def __str__(self) -> str:
      return f"Interface not found for {self.survey_id}"

ZTF_SURVEY_ID = "ztf"
ATLAS_SURVEY_ID = "atlas"

DATABASE_INTERFACES = {
  ZTF_SURVEY_ID: PSQLInterface,
  ATLAS_SURVEY_ID: MongoInterface
}

class BaseCommand(object):

  def __init__(self, survey_id) -> None:
    self.survey_id = survey_id

  def database_interface_selector(self):
    db_interface = DATABASE_INTERFACES.get(self.survey_id)

    if db_interface:
      return db_interface()
    else:
      raise InterfaceNotFound(self.survey_id)

class GetLightCurve(BaseCommand):

  def __init__(self, object_id, survey_id) -> None:
    super().__init__(survey_id)
    self.object_id = object_id
    self.database_interface = self.database_interface_selector()
  
  def execute(self):
    return self.database_interface.get_light_curve(self.object_id)


class GetDetections(BaseCommand):

  def __init__(self, object_id, survey_id) -> None:
    super().__init__(survey_id)
    self.object_id = object_id
    self.database_interface = self.database_interface_selector()
  
  def execute(self):
    return self.database_interface.get_detections(self.object_id)


class GetNonDetections(BaseCommand):

  def __init__(self, object_id, survey_id) -> None:
    super().__init__(survey_id)
    self.object_id = object_id
    self.database_interface = self.database_interface_selector()
  
  def execute(self):
    return self.database_interface.get_non_detections(self.object_id)
