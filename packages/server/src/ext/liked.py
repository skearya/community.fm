from discord import Interaction, app_commands
from discord.ext import commands
from main import CustomBot


class LikedSongs(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(description="?")
    @app_commands.guild_only()
    async def cmd(self, interaction: Interaction):
        pass


async def setup(bot: CustomBot):
    await bot.add_cog(LikedSongs(bot))
