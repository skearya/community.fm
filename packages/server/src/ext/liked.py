from discord import Interaction, app_commands
from discord.ext import commands
from main import CustomBot

# TODO: read channel on startup, get csvs from newest members
# standardize channel name so it works per server "liked-songs"
# read new messages added to the channel

class LikedSongs(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(description="?")
    @app_commands.guild_only()
    async def cmd(self, interaction: Interaction):
        pass


async def setup(bot: CustomBot):
    await bot.add_cog(LikedSongs(bot))
