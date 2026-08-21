import asyncio
from dataclasses import fields
from io import BytesIO
from itertools import islice

import discord
from bot import CustomBot
from discord import Interaction, Member, app_commands
from discord.ext import commands
from loguru import logger
from utils import header


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

        url = f"{self.bot.state.config.ICECAST_BASE_URL}/stream.ogg"

        vc.play(
            discord.FFmpegPCMAudio(url),
            after=lambda e: logger.error(f"Discord player error: {e}") if e else None,
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
        self, _interaction: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        manager = self.bot.state.manager

        choices: list[app_commands.Choice] = []

        for mode in manager.modes:
            name = f"{mode.name} ({mode.mode})"

            if current in name:
                choices.append(app_commands.Choice(name=name, value=mode.name))

        return choices

    @app_commands.command(description="Get or set the current radio mode.")
    @app_commands.autocomplete(name=mode_autocomplete)
    @app_commands.guild_only()
    async def mode(self, interaction: Interaction, name: str | None):
        manager = self.bot.state.manager

        if name is None:
            await interaction.response.send_message(
                f"Currently in the '{manager.mode.name}' mode."
            )
            return

        if await manager.switch(name):
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
        entry = self.bot.state.liquidsoap.value

        embed = discord.Embed(title=header(entry.metadata))

        for key in fields(entry.metadata):
            value = getattr(entry.metadata, key.name)

            if (
                value is None
                or len(value) > 512
                or key.name == "cover"
                or key.name == "avatar"
            ):
                continue

            embed.add_field(name=key.name, value=value)

        if entry.cover:
            mime, bytes = entry.cover

            match mime.split("/", 1):
                case ["image", extension]:
                    filename = f"cover.{extension}"
                    file = discord.File(BytesIO(bytes), filename)
                    embed.set_thumbnail(url=f"attachment://{filename}")

                    await interaction.response.send_message(file=file, embed=embed)
                    return

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="recently-played", description="See recently played tracks from the radio."
    )
    @app_commands.guild_only()
    async def recently_played(self, interaction: Interaction):
        lines: list[str] = []

        for entry in islice(self.bot.state.history, 0, 10):
            details = " • ".join(
                filter(
                    None,
                    [
                        f"<t:{int(entry.time)}:t>",
                        entry.metadata.album and f"*{entry.metadata.album}*",
                        entry.metadata.user and f"*{entry.metadata.user}*",
                    ],
                )
            )

            lines.append(
                f"**{entry.metadata.title or 'Unknown Artist'}** - {entry.metadata.artist or 'Unknown Title'}\n"
                f"-# {details}",
            )

        embed = discord.Embed(
            title="Recently played", description="\n".join(lines) or "..."
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Skip the currently playing song on the radio.")
    @app_commands.guild_only()
    async def skip(self, interaction: Interaction):
        async with self.bot.state.session.post(
            f"{self.bot.state.config.LIQUIDSOAP_BASE_URL}/skip"
        ) as response:
            response.raise_for_status()

            await interaction.response.send_message("Skipped.")

    async def status_updater(self):
        async with self.bot.state.liquidsoap.subscribe() as queue:
            while True:
                entry = await queue.get()

                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=header(entry.metadata),
                )

                try:
                    await self.bot.change_presence(activity=activity)
                except Exception as e:
                    logger.error(f"Discord status error: {e}")


async def setup(bot: CustomBot):
    await bot.add_cog(Stream(bot))
