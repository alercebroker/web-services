
class BadSettingException(Exception):
    def __init__(self, settings_errors):
        self.settings_errors = settings_errors
    
    def __str__(self):
        return ", ".join(self.settings_errors)

class MissingFilterException(Exception):
    def __init__(self, filter_list):
        self.missing_filters = filter_list
    
    def __str__(self):
        formated_result = [
            f"Missing filter {filter}"
            for filter in self.missing_filters
        ]
        return ", ".join(formated_result)

class FilterExecutionException(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
    
    def __str__(self):
        return str(self.original_exception)

class ClientRequestException(Exception):
    def __init__(self, code):
        self.code = code
    
    def __str__(self):
        return f"Resquest failed code: {self.code}"
