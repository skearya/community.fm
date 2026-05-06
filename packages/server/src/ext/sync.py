import discord
from bot import CustomBot
from discord import Interaction, app_commands
from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(description="Sync bot commands locally.")
    @app_commands.guild_only()
    async def sync(self, interaction: Interaction):
        assert self.bot.state.config.DISCORD_TEST_GUILD
        DISCORD_TEST_GUILD = discord.Object(id=self.bot.state.config.DISCORD_TEST_GUILD)

        self.bot.tree.copy_global_to(guild=DISCORD_TEST_GUILD)
        await self.bot.tree.sync(guild=DISCORD_TEST_GUILD)

        await interaction.response.send_message("Synced.")


async def setup(bot: CustomBot):
    await bot.add_cog(Sync(bot))
