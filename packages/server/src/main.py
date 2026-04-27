import asyncio

import bot
import server
from state import State


async def main():
    async with State() as state:
        await asyncio.gather(server.start(state), bot.start(state))


if __name__ == "__main__":
    asyncio.run(main())
