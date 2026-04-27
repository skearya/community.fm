from os import environ

import aiohttp
import discord
from discord import Intents
from discord.ext import commands
from loguru import logger
from state import State

TEST_GUILD = discord.Object(id=environ["DISCORD_TEST_GUILD"])


class CustomBot(commands.Bot):
    def __init__(self, state: State):
        intents = Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
        )

        self.state = state
        self.session = aiohttp.ClientSession()

    async def setup_hook(self):
        await self.load_extension("ext.stream")
        await self.load_extension("ext.liked")

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def close(self):
        await self.session.close()
        await super().close()


async def start(state: State):
    discord.utils.setup_logging()

    async with CustomBot(state) as bot:
        await bot.start(environ["DISCORD_BOT_TOKEN"])
