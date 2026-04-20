import discord
from discord import Interaction, Member, app_commands
from discord.ext import commands
from main import CustomBot

STREAM_URL = "https://radio.isabitch.lol/stream.ogg"


class Stream(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    async def join(self, interaction: Interaction):
        assert interaction.guild is not None
        assert isinstance(interaction.user, Member)

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect(force=True)

        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("You aren't in a voice channel.")
            return

        vc = await interaction.user.voice.channel.connect()
        await interaction.response.send_message("Joined.")

        vc.play(
            discord.FFmpegPCMAudio(STREAM_URL),
            after=lambda e: print(f"Player error: {e}") if e else None,
        )

    @app_commands.command()
    @app_commands.guild_only()
    async def leave(self, interaction: Interaction):
        assert interaction.guild is not None
        assert isinstance(interaction.user, Member)

        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                "I'm not currently in a voice channel."
            )
            return

        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("Left.")


async def setup(bot: CustomBot):
    await bot.add_cog(Stream(bot))
