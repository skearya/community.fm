from os import environ

import discord
from discord import Intents
from discord.ext import commands

TEST_GUILD = discord.Object(id=environ["DISCORD_TEST_GUILD"])


class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=Intents.default(),
        )

    async def setup_hook(self):
        await self.load_extension("ext.stream")

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
