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



class OidError(BaseException):
    def __init__(self, oid) -> None:
        super().__init__()
        self.oid = oid

    def __str__(self) -> str:
        return f"Can't retrieve magstats oid not recognized {self.oid}"
