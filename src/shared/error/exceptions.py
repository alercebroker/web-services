class WrapperException(BaseException):
    def __init__(self, original_e, subcode=None):
        super().__init__()
        self.original_exception = original_e
        self.subcode = subcode

    def __str__(self) -> str:
        return self.original_exception.__str__()


class ClientErrorException(WrapperException):
    def __init__(self, original_e, subcode=None):
        super().__init__(original_e, subcode)


class ServerErrorException(WrapperException):
    def __init__(self, original_e, subcode=None):
        super().__init__(original_e, subcode)


class ObjectNotFound(BaseException):
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


class InterfaceNotFound(BaseException):
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
