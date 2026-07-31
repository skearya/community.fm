from pathlib import Path

import discord
from discord import Intents
from discord.ext import commands
from loguru import logger
from state import State
from utils import InterceptHandler


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
        await self.load_extension("ext.queue")
        await self.load_extension("ext.reload")
        await self.load_extension("ext.channel")
        await self.load_extension("ext.lastfm")

        if self.state.config.PROD:
            if DISCORD_TEST_GUILD := self.state.config.DISCORD_TEST_GUILD:
                guild = discord.Object(id=DISCORD_TEST_GUILD)

                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)

            await self.tree.sync()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def close(self):
        await super().close()


async def start(state: State):
    if not (DISCORD_BOT_TOKEN := state.config.DISCORD_BOT_TOKEN):
        return

    discord.utils.setup_logging(handler=InterceptHandler(), root=False)

    if Path("/usr/lib/libopus.so").exists():
        discord.opus.load_opus("/usr/lib/libopus.so")

    async with CustomBot(state) as bot:
        await bot.start(DISCORD_BOT_TOKEN)
