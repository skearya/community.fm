from discord import Interaction, app_commands, VoiceChannel
from discord.ext import commands

from main import CustomBot


class General(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command()
    async def hello(self, interaction: Interaction):
        await interaction.response.send_message(f"Hello Bro {interaction.user.mention}")

    @app_commands.command()
    async def join(self, interaction: Interaction, channel: VoiceChannel):
        if interaction.guild is None:
            await interaction.response.send_message("Run this command in a server.")
            return

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect(force=True)

        await channel.connect()
        await interaction.response.send_message("Joined.")

    @app_commands.command()
    async def leave(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Run this command in a server.")
            return

        if interaction.guild.voice_client is None:
            await interaction.response.send_message("Not currently in a voice channel.")
            return

        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("Left.")


async def setup(bot: CustomBot):
    await bot.add_cog(General(bot))
