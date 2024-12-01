from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(data) -> dict:
        raise NotImplementedError
