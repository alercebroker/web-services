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



class SurveyIdError(BaseException):
    def __init__(self, survey_id) -> None:
        super().__init__()
        self.survey_id = survey_id

    def __str__(self) -> str:
        return f"Can't retrieve magstats survey id not recognized {self.survey_id}"
