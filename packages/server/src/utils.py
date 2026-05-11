import asyncio
import inspect
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger


class Subscribable[T]:
    value: T | None
    subscribers: set[asyncio.Queue[T]]

    def __init__(self, initial: T | None = None):
        self.value = initial
        self.subscribers = set()

    def update(self, value: T) -> None:
        if value == self.value:
            return

        self.value = value

        for subscriber in self.subscribers:
            subscriber.put_nowait(value)

    @asynccontextmanager
    async def subscribe(self) -> AsyncGenerator[asyncio.Queue[T]]:
        queue = asyncio.Queue[T]()
        self.subscribers.add(queue)

        try:
            yield queue
        finally:
            self.subscribers.remove(queue)


# https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
