from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from models import LiquidsoapUri

if TYPE_CHECKING:
    from state import State


class RadioMode(ABC):
    def __init__(self, name: str, state: State):
        self.name = name
        self.state = state

    @abstractmethod
    async def setup(self) -> None:
        """Sets up the mode on server startup."""
        pass

    @abstractmethod
    async def next(self) -> LiquidsoapUri | None:
        """Returns the URI of the next song."""
        pass
