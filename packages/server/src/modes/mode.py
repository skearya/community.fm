from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from models import LiquidsoapUri

if TYPE_CHECKING:
    from state import State


class RadioMode(ABC):
    @abstractmethod
    def options() -> type[Any]:
        """Returns a `TypedDict` class of options that will be passed to the constructor."""

    def __init__(self, state: State, mode: str, name: str):
        self.state = state
        self.mode = mode
        self.name = name

    @abstractmethod
    async def setup(self) -> None:
        """Sets up the mode on server startup."""

    @abstractmethod
    async def reload(self) -> None:
        """Reloads any data that needs to be refreshed."""

    @abstractmethod
    async def next(self) -> LiquidsoapUri | None:
        """Returns the URI of the next song."""
