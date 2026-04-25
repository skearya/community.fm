from abc import ABC, abstractmethod

class RadioMode(ABC):
    @abstractmethod
    def next() -> str:
        """Returns the URI of the next song."""
        pass

    