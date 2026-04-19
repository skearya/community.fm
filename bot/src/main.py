import asyncio
from os import environ

import discord
from discord import Intents
from discord.ext import commands

TEST_GUILD = discord.Object(id=environ.get("TEST_GUILD", "?"))


class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=Intents.default(),
        )

    async def setup_hook(self):
        await self.load_extension("ext.general")

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    async def on_ready(self):
        print(f"Logged in as {self.user}")


async def main():
    async with CustomBot() as bot:
        await bot.start(environ.get("BOT_TOKEN", "?"))


if __name__ == "__main__":
    asyncio.run(main())
