import base64
import re
from io import BytesIO
from os import environ

import discord
from bot import CustomBot
from discord import Interaction, Member, app_commands
from discord.ext import commands

STREAM_URL = environ["RADIO_STREAM_URL"]


class Stream(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @app_commands.command(description="Start playing the radio in the VC you're in.")
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

    @app_commands.command(description="Stop playing the radio.")
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

    @app_commands.command(
        name="now-playing", description="Get the currently playing song on the radio."
    )
    @app_commands.guild_only()
    async def now_playing(self, interaction: Interaction):
        metadata = self.bot.state.metadata

        if metadata is None:
            await interaction.response.send_message(
                "The radio is currently initializing, or something is going very wrong."
            )
            return

        embed = discord.Embed(
            title=f"{metadata.get('artist', 'Unknown Artist')} - {metadata.get('title', 'Unknown Title')}"
        )

        for k, v in metadata.items():
            if k == "cover" or len(v) > 1024:
                continue

            embed.add_field(name=k, value=v)

        if cover := metadata.get("cover"):
            match cover.split(","):
                case [header, data] if match := re.search(
                    "data:image/(.*);base64", header
                ):
                    extension = match.group(1)
                    decoded = base64.b64decode(data)

                    filename = f"cover.{extension}"
                    file = discord.File(fp=BytesIO(decoded), filename=filename)
                    embed.set_thumbnail(url=f"attachment://{filename}")

                    await interaction.response.send_message(file=file, embed=embed)

        await interaction.response.send_message(embed=embed)


async def setup(bot: CustomBot):
    await bot.add_cog(Stream(bot))
