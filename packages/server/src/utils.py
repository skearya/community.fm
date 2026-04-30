import asyncio
from contextlib import asynccontextmanager


class Subscribable[T]:
    value: T | None
    subscribers: set[asyncio.Queue[T]]

    def __init__(self, initial: T | None = None):
        self.value = initial
        self.subscribers = set()

    def update(self, value: T):
        self.value = value

        for subscriber in self.subscribers:
            subscriber.put_nowait(value)

    @asynccontextmanager
    async def subscribe(self):
        queue = asyncio.Queue[T]()
        self.subscribers.add(queue)

        try:
            yield queue
        finally:
            self.subscribers.remove(queue)
