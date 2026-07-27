import hashlib
import json
from dataclasses import asdict

import discord
from bot import CustomBot
from cachetools import LRUCache
from discord import Interaction, Member, User, app_commands
from discord.ext import commands
from models import RequestQueueModeEntry
from modes.queue import RequestQueueMode
from pls import Album, Media, MediaType, Playlist, Summary, Track


class Queue(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.summaries: LRUCache[str, Summary] = LRUCache(maxsize=512)

    @app_commands.command(
        name="queue-url", description="Queue a song onto the radio from a URL."
    )
    @app_commands.describe(url="YouTube/Qobuz/Tidal/Deezer/Soundcloud supported")
    @app_commands.guild_only()
    async def queue_url(self, interaction: Interaction, url: str):
        if not (queue := await self.default(interaction)):
            return

        await interaction.response.defer()

        if not (media := await self.bot.state.pls.url(url)):
            await interaction.followup.send(
                "I failed to fetch needed metadata from this URL. Are you using a supported service (YouTube/Qobuz/Tidal/Deezer/Soundcloud)?",
                ephemeral=True,
            )
            return

        embed = await self.process(queue, interaction.user, media)
        await interaction.followup.send(embed=embed)

    async def query_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        type = interaction.namespace.type
        service = interaction.namespace.service

        if not type or not current:
            return []

        results = await self.bot.state.pls.search(
            query=current,
            type=type,
            services=[service] if service else None,
        )

        choices: list[app_commands.Choice] = []

        for _score, summary in results[:25]:
            string = json.dumps(asdict(summary), sort_keys=True)
            hash = hashlib.md5(string.encode("utf-8")).hexdigest()

            self.summaries[hash] = summary

            name = f"{summary.id[0]} | {summary.artist} - {summary.title}"
            value = hash

            choices.append(app_commands.Choice(name=name[:100], value=value))

        return choices

    async def service_autocomplete(
        self, _interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=service, value=service)
            for service in self.bot.state.pls.services()
            if current in service
        ]

    @app_commands.command(
        name="queue-search",
        description="Queue a song onto the radio through searching.",
    )
    @app_commands.describe(
        type="track or album or playlist", query="'artist' - 'title' recommended"
    )
    @app_commands.autocomplete(query=query_autocomplete, service=service_autocomplete)
    @app_commands.guild_only()
    async def queue_search(
        self,
        interaction: Interaction,
        type: MediaType,
        query: str,
        service: str | None = None,
    ):
        if not (queue := await self.default(interaction)):
            return

        await interaction.response.defer()

        if not (
            summary := self.summaries.get(query)
            or await self.bot.state.pls.best(
                query, type, [service] if service else None
            )
        ):
            await interaction.followup.send(
                "I failed to find a close enough match, try selecting an autocomplete option or queuing a URL."
            )
            return

        if not (media := await self.bot.state.pls.info(*summary.id, summary.type)):
            await interaction.followup.send(
                f"I failed to fetch needed metadata for {summary.title} by {summary.artist} ({summary.id[0]}), please try another service."
            )
            return

        embed = await self.process(queue, interaction.user, media)
        await interaction.followup.send(embed=embed)

    @app_commands.command(description="See the current tracks in queue.")
    @app_commands.guild_only()
    async def queue(self, interaction: Interaction):
        if not (queue := await self.default(interaction)):
            return

        lines: list[str] = []

        for entry in queue.items:
            details = " • ".join(
                filter(
                    None,
                    [
                        entry.track.id and f"*{entry.track.id[0]}*",
                        f"*{entry.username}*",
                    ],
                )
            )

            lines.append(
                f"**{entry.track.title or 'Unknown'}** by {entry.track.artist or 'Unknown'}\n"
                f"-# {details}",
            )

        embed = discord.Embed(title="Queue", description="\n".join(lines) or "...")

        await interaction.response.send_message(embed=embed)

    async def process(
        self, queue: RequestQueueMode, user: User | Member, media: Media
    ) -> discord.Embed:
        embed = discord.Embed()

        if isinstance(media, Track):
            assert media.id

            embed.title = "Track queued"
            embed.description = f"### {media.title} by {media.artist}"
            embed.set_footer(text=f"{media.id[0]}: {media.id[1]}")

            if media.url:
                embed.url = media.url

            queue.items.append(
                RequestQueueModeEntry(user.display_name, user.display_avatar.url, media)
            )
        elif isinstance(media, Album | Playlist):
            embed.title = "Album queued"
            embed.description = (
                f"### {media.title} by {media.artist}\n"
                if isinstance(media, Album)
                else f"### {media.title}\n"
            ) + (
                "\n".join(
                    [
                        f"-# {track.title or 'Unknown'} by {track.artist or 'Unknown'}"
                        for track in media.items
                    ]
                )
            )

            embed.set_footer(
                text=", ".join({track.id[0] for track in media.items if track.id})
            )

            if isinstance(media, Album) and media.cover:
                embed.set_thumbnail(url=media.cover)

            queue.items.extend(
                [
                    RequestQueueModeEntry(
                        user.display_name, user.display_avatar.url, track
                    )
                    for track in media.items
                ]
            )

        manager = self.bot.state.manager

        if queue.autoswitch and manager.mode is not queue:
            await manager.switch(queue.name)

        return embed

    async def default(self, interaction: Interaction) -> RequestQueueMode | None:
        for mode in self.bot.state.manager.modes:
            if isinstance(mode, RequestQueueMode):
                return mode

        await interaction.response.send_message(
            "There aren't any request queues defined in the current radio configuration!"
        )

        return None


async def setup(bot: CustomBot):
    await bot.add_cog(Queue(bot))
