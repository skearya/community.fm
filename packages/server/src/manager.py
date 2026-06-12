import asyncio
import os
import random
import tomllib
import typing
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from loguru import logger
from models import LiquidsoapUri
from modes.channel import ChannelMode
from modes.lastfm import LastFMMode
from modes.local import LocalSongsMode
from modes.mode import RadioMode
from modes.queue import RequestQueueMode
from modes.youtube import YoutubeMode
from utils import ConfigError, quoted

if TYPE_CHECKING:
    from state import State

RETRIES_BEFORE_MODE_SWITCH = 3
DOWNLOADS_BEFORE_DELETION = 3

MODE_CONSTRUCTORS = {
    "youtube": YoutubeMode,
    "last-fm": LastFMMode,
    "channel": ChannelMode,
    "queue": RequestQueueMode,
    "local": LocalSongsMode,
}


class Request:
    def __init__(self, mode: RadioMode):
        self.mode = mode
        self.task = asyncio.create_task(mode.next())
        self.retries = 0

    def retry(self):
        logger.debug(
            f"Retrying request for mode {self.mode.name} ({self.retries + 1}/{RETRIES_BEFORE_MODE_SWITCH})"
        )

        self.task = asyncio.create_task(self.mode.next())
        self.retries += 1


class ModeManager:
    def __init__(self, state: State):
        self.state = state
        self.modes = config(state)
        self.mode = random.choice(
            [m for m in self.modes if not isinstance(m, RequestQueueMode)]
        )

        self.request: Request | None = None
        self.history: deque[LiquidsoapUri] = deque()
        self.reloading = asyncio.Lock()

    async def setup(self) -> None:
        for mode in self.modes:
            await mode.setup()

    async def reload(self, modes: list[str] | None = None) -> bool:
        if self.reloading.locked():
            return False

        name = ", ".join(quoted(modes)) if modes else "all"

        logger.debug(f"Reloading {name} modes.")

        async with self.reloading:
            for mode in self.modes:
                if modes and mode.name not in modes:
                    continue

                await mode.reload()

        logger.debug(f"Reloaded {name} modes.")

        return True

    async def switch(self, name: str) -> bool:
        match = next((m for m in self.modes if m.name == name), None)

        if match is None:
            return False

        old, self.mode = self.mode, match
        logger.info(f"Mode switched from '{old.name}' to '{match.name}'")

        if self.request is not None:
            self.request.task.cancel()

            try:
                await self.request.task
            except asyncio.CancelledError:
                pass

            self.request = Request(self.mode)

        async with self.state.session.post(
            f"{self.state.config.LIQUIDSOAP_BASE_URL}/clear"
        ) as response:
            response.raise_for_status()

        return True

    def next(self) -> str:
        match self.request:
            case Request() if self.request.task.done():
                if (
                    not self.request.task.cancelled()
                    and self.request.task.exception() is None
                    and (dl := self.request.task.result())
                ):
                    logger.info(f"Serving {dl.file} from '{self.request.mode.name}'")

                    dl.metadata["mode"] = self.request.mode.name
                    self.request = None

                    self.history.append(dl)

                    if len(self.history) > DOWNLOADS_BEFORE_DELETION:
                        old = self.history.popleft()

                        if old.deletable:
                            Path(old.file).unlink(missing_ok=True)

                    return str(dl)

                if self.request.retries + 1 >= RETRIES_BEFORE_MODE_SWITCH:
                    mode = random.choice(
                        [m for m in self.modes if m is not self.request.mode]
                    )

                    logger.warning(
                        f"Mode '{self.request.mode.name}' consistently failed, trying '{mode.name}'"
                    )

                    self.mode = mode
                    self.request = Request(self.mode)
                else:
                    self.request.retry()

                return "LOADING"
            case Request():
                return "LOADING"
            case None:
                self.request = Request(self.mode)

                return "LOADING"


def config(state: State) -> list[RadioMode]:
    text = Path(state.config.CONFIG_FILEPATH).read_text()

    expanded = os.path.expandvars(text)
    config = tomllib.loads(expanded)

    if "modes" not in config:
        raise ConfigError("Expected 'modes' in config, see example config")

    if not isinstance(config["modes"], dict):
        raise ConfigError(
            "Expected 'modes' in config to be an dictionary, see example config"
        )

    modes: list[RadioMode] = []

    for mode, instances in config["modes"].items():
        assert isinstance(mode, str)

        if not isinstance(instances, dict):
            raise ConfigError(
                f"Expected 'modes.{mode}' to be an dictionary, see example config"
            )

        if not (constructor := MODE_CONSTRUCTORS.get(mode)):
            raise ConfigError(
                f"Unexpected mode 'modes.{mode}', available modes are {', '.join(quoted(MODE_CONSTRUCTORS.keys()))}"
            )

        annotations = typing.get_type_hints(constructor.options())

        for name, options in instances.items():
            assert isinstance(name, str)

            if not isinstance(options, dict):
                raise ConfigError(
                    f"Expected 'modes.{mode}.{name}' to be an dictionary, see example config"
                )

            options = {k.replace("-", "_"): v for k, v in options.items()}

            validate(f"modes.mode.{name}", options, annotations)

            modes.append(constructor(state, name, typing.cast(Any, options)))

    return modes


def validate(path: str, options: dict[Any, Any], annotations: dict[str, Any]):
    for key, expected in annotations.items():
        if key not in options:
            raise ConfigError(
                f"In '{path}': Missing key '{key}' with type '{expected}'"
            )

    for key, value in options.items():
        if not (expected := annotations.get(key)):
            raise ConfigError(
                f"In '{path}': Unexpected key '{key}' in {options}, expected shape is '{annotations}'"
            )

        if typing.get_origin(expected) is Literal:
            values = typing.get_args(expected)

            if value not in values:
                raise ConfigError(
                    f"In '{path}': Expected key '{key}' with value '{value}' to be one of {','.join(quoted(values))}"
                )
        elif not isinstance(value, expected):
            raise ConfigError(
                f"In '{path}': Expected key '{key}' with value '{value}' to be of type '{expected}'"
            )
