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


class NonDetectionsNotFound(BaseException):
    def __init__(self, object_id) -> None:
        super().__init__()
        self.object_id = object_id

    def __str__(self) -> str:
        return f"Non Detections not found for object {self.object_id} on SQL Database"
