

class ObjectNotFound(Exception):
    def __init__(self, message="Object not found"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"