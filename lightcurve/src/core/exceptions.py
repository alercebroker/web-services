class WrapperException(BaseException):
    def __init__(self, original_e, subcode=None):
        super().__init__()
        self.original_exception = original_e
        self.subcode = subcode

    def __str__(self) -> str:
        return self.original_exception.__str__()


class DatabaseError(WrapperException):
    def __init__(self, original_e, subcode=None):
        super().__init__(original_e, subcode)


class DetectionsNotFound(BaseException):
    def __init__(self, object_id) -> None:
        super().__init__()
        self.object_id = object_id

    def __str__(self) -> str:
        return (
            f"Detections not found for object {self.object_id} on SQL Database"
        )


class ObjectNotFound(BaseException):
    def __init__(self, object_id) -> None:
        super().__init__()
        self.object_id = object_id

    def __str__(self) -> str:
        return (
            f"Object {self.object_id} not found on the database"
        )


class NonDetectionsNotFound(BaseException):
    def __init__(self, object_id) -> None:
        super().__init__()
        self.object_id = object_id

    def __str__(self) -> str:
        return f"Non Detections not found for object {self.object_id} on SQL Database"


class SurveyIdError(BaseException):
    def __init__(self, survey_id) -> None:
        super().__init__()
        self.survey_id = survey_id

    def __str__(self) -> str:
        return f"Can't retrieve detections survey id not recognized {self.survey_id}"


class AtlasNonDetectionError(BaseException):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return "Can't retrieve non detections: ATLAS does not provide non_detections"
