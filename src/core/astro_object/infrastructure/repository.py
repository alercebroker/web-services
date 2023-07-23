from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def get(payload):
        pass
