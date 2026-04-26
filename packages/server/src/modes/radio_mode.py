from abc import ABC, abstractmethod


class RadioMode(ABC):
    @abstractmethod
    async def next(self) -> str:
        """Returns the URI of the next song."""
        pass
