from os import environ
from pathlib import Path

import discord
from discord import Intents
from discord.ext import commands
from loguru import logger
from state import State
from utils import InterceptHandler

TEST_GUILD = discord.Object(id=environ["DISCORD_TEST_GUILD"])
BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]


class CustomBot(commands.Bot):
    def __init__(self, state: State):
        intents = Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
        )

        self.state = state

    async def setup_hook(self):
        await self.load_extension("ext.stream")
        await self.load_extension("ext.liked")
        await self.load_extension("ext.sync")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def close(self):
        await super().close()


async def start(state: State):
    discord.utils.setup_logging(handler=InterceptHandler(), root=False)

    if Path("/usr/lib/libopus.so").exists():
        discord.opus.load_opus("/usr/lib/libopus.so")

    async with CustomBot(state) as bot:
        await bot.start(BOT_TOKEN)
