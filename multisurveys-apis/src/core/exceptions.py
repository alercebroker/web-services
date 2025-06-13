class WrapperException(BaseException):
    def __init__(self, original_e, subcode=None):
        super().__init__()
        self.original_exception = original_e
        self.subcode = subcode

    def __str__(self) -> str:
        return self.original_exception.__str__()


class DatabaseError(WrapperException):
    def __init__(self, original_e, database: str, subcode=None):
        self.database = database
        super().__init__(original_e, subcode)

    def __str__(self) -> str:
        return f"{self.database} error: {self.original_exception.__str__()}"
