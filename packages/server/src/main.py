import asyncio

import bot
import server


async def main():
    await asyncio.gather(
        server.start(),
        bot.start()
    )


if __name__ == "__main__":
    asyncio.run(main())
