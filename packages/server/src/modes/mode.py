from abc import ABC, abstractmethod


class RadioMode(ABC):
    @abstractmethod
    def name(self) -> str:
        """Returns a label for the mode."""
        pass

    @abstractmethod
    async def setup(self) -> None:
        """Sets up the mode on server startup."""
        pass

    @abstractmethod
    async def next(self) -> str:
        """Returns the URI of the next song."""
        pass
