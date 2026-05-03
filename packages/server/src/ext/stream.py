import asyncio
import base64
import re
from dataclasses import fields
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
        self.status_task = asyncio.create_task(self.status_updater())

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

    async def mode_autocomplete(
        self, _interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=mode.name(), value=mode.name())
            for mode in self.bot.state.modes
            if current in mode.name()
        ]

    @app_commands.command(description="Get or set the current radio mode.")
    @app_commands.autocomplete(name=mode_autocomplete)
    @app_commands.guild_only()
    async def mode(self, interaction: Interaction, name: str | None):
        if name is None:
            await interaction.response.send_message(
                f"Currently in the '{self.bot.state.mode.name()}' mode."
            )
            return

        match = next(
            (mode for mode in self.bot.state.modes if mode.name() == name), None
        )

        if mode := match:
            self.bot.state.mode = mode
            await interaction.response.send_message(f"Set mode to {name}.")
        else:
            await interaction.response.send_message(
                f"I couldn't find a mode with the name '{name}'."
            )

    @app_commands.command(
        name="now-playing", description="Get the currently playing song on the radio."
    )
    @app_commands.guild_only()
    async def now_playing(self, interaction: Interaction):
        metadata = self.bot.state.metadata.value

        if metadata is None:
            await interaction.response.send_message(
                "The radio is currently initializing, or something is going very wrong."
            )
            return

        embed = discord.Embed(
            title=f"{metadata.artist or 'Unknown Artist'} - {metadata.title or 'Unknown Title'}"
        )

        for key in fields(metadata):
            value = getattr(metadata, key.name)

            if value is None or len(value) > 1024 or key.name == "cover":
                continue

            embed.add_field(name=key.name, value=value)

        if cover := metadata.cover:
            match cover.split(","):
                case [header, data] if match := re.search(
                    "data:image/(.*);base64", header
                ):
                    extension = match.group(1)
                    decoded = base64.b64decode(data)

                    filename = f"cover.{extension}"
                    file = discord.File(BytesIO(decoded), filename)
                    embed.set_thumbnail(url=f"attachment://{filename}")

                    await interaction.response.send_message(file=file, embed=embed)
                    return

        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Skip the currently playing song on the radio.")
    @app_commands.guild_only()
    async def skip(self, interaction: Interaction):
        async with self.bot.state.session.post("/skip") as response:
            response.raise_for_status()

            await interaction.response.send_message("Skipped.")

    async def status_updater(self):
        async with self.bot.state.metadata.subscribe() as queue:
            while True:
                metadata = await queue.get()

                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"{metadata.artist or 'Unknown Artist'} - {metadata.title or 'Unknown Title'}",
                )

                try:
                    await self.bot.change_presence(activity=activity)
                except Exception:
                    pass


async def setup(bot: CustomBot):
    await bot.add_cog(Stream(bot))
