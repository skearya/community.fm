import asyncio
import base64
import hashlib
import json
import re
from dataclasses import asdict, fields
from io import BytesIO

import discord
from bot import CustomBot
from discord import Interaction, Member, app_commands
from discord.ext import commands
from loguru import logger
from pls import Album, MediaType, Playlist, Summary, Track


class Stream(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.status_task = asyncio.create_task(self.status_updater())
        self.autocomplete_to_summary: dict[str, Summary] = {}

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
        self, _interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        manager = self.bot.state.manager

        return [
            app_commands.Choice(name=mode.name, value=mode.name)
            for mode in manager.modes
            if current in mode.name
        ]

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

    async def queue_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        pls = self.bot.state.pls

        if not interaction.namespace.type or not current:
            return []

        results = await pls.search(
            title=None, artist=None, query=current, type=interaction.namespace.type
        )

        choices: list[app_commands.Choice] = []

        for summary in results[:25]:
            string = json.dumps(asdict(summary), sort_keys=True)
            hash = hashlib.md5(string.encode("utf-8")).hexdigest()

            self.autocomplete_to_summary[hash] = summary

            name = f"{summary.id[0].capitalize()} | {summary.artist} - {summary.title}"
            value = hash

            choices.append(app_commands.Choice(name=name[:100], value=value))

        return choices

    @app_commands.command(
        name="queue-search",
        description="Queue a song onto the radio through searching.",
    )
    @app_commands.describe(
        type="track or album or playlist",
        query="'artist' - 'title' recommended",
    )
    @app_commands.autocomplete(query=queue_autocomplete)
    @app_commands.guild_only()
    async def queue(
        self,
        interaction: Interaction,
        type: MediaType,
        query: str,
    ):
        pls = self.bot.state.pls
        manager = self.bot.state.manager

        summary = self.autocomplete_to_summary.get(query)

        if summary is None:
            await interaction.response.send_message(
                "Please use the autocomplete menu to select an option.", ephemeral=True
            )
            return

        media = await pls.info(*summary.id, summary.type)

        if media is None:
            await interaction.response.send_message(
                f"I failed to fetch needed metadata for {summary.title} by {summary.artist} from {summary.id}, please try another service."
            )
            return

        embed = discord.Embed()

        match media:
            case Track():
                embed.title = "Track added"
                embed.description = (
                    f"{media.artist} - {media.title} ({': '.join([*summary.id])})"
                )

                manager.queue.items.append(media)
            case Album():
                embed.title = "Album added"
                embed.description = "\n".join(
                    [
                        f"{media.artist} - {media.title} ({': '.join([*summary.id])})",
                        *[track.title or "Unknown" for track in media.items],
                    ]
                )

                if media.cover:
                    embed.set_thumbnail(url=media.cover)

                manager.queue.items.extend(media.items)
            case Playlist():
                embed.title = "Playlist added"
                embed.description = "\n".join(
                    [
                        f"{media.title} ({': '.join([*summary.id])})",
                        *[track.title or "Unknown" for track in media.items],
                    ]
                )

                manager.queue.items.extend(media.items)

        await interaction.response.send_message(embed=embed)

        if manager.mode is manager.queue:
            return

        await manager.switch(manager.queue.name)

        # if manager.mode is manager.queue:
        #     await interaction.response.send_message("Added to queue.")
        # else:
        #     await interaction.response.send_message(
        #         "Added to queue. To play from the queue, set the mode to 'Request Queue' using `/mode`."
        #     )

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

    @app_commands.command(
        name="recently-played", description="See recently played tracks from the radio."
    )
    @app_commands.guild_only()
    async def recently_played(self, interaction: Interaction):
        lines: list[str] = []

        for metadata, time in self.bot.state.metadata_history:
            details = " • ".join(
                filter(
                    None,
                    [
                        f"<t:{int(time)}:t>",
                        metadata.album and f"*{metadata.album}*",
                        metadata.user and f"*{metadata.user}*",
                    ],
                )
            )

            lines.append(
                f"**{metadata.title or 'Unknown'}** by {metadata.artist or 'Unknown'}\n"
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
