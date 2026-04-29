from os import environ

import discord
from bot import CustomBot
from discord import Interaction, app_commands
from discord.ext import commands

TEST_GUILD = discord.Object(id=environ["DISCORD_TEST_GUILD"])


class Sync(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(description="Sync bot commands locally.")
    @app_commands.guild_only()
    @app_commands.guilds(TEST_GUILD)
    async def sync(self, interaction: Interaction):
        self.bot.tree.copy_global_to(guild=TEST_GUILD)
        await self.bot.tree.sync(guild=TEST_GUILD)

        await interaction.response.send_message("Synced.")


async def setup(bot: CustomBot):
    await bot.add_cog(Sync(bot))
